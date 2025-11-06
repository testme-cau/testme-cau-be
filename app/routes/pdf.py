"""
PDF routes (file upload and management) - FastAPI version
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from firebase_admin import firestore

from app.dependencies.auth import get_current_user
from app.services.firebase_storage import FirebaseStorageService
from app.utils.file_utils import allowed_file
from app.models.responses import PDFUploadResponse, PDFListResponse, PDFInfo, SuccessResponse
from config import settings

router = APIRouter(tags=["pdf"])


@router.post("/upload", response_model=PDFUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to upload"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload PDF file to Firebase Storage
    
    - **file**: PDF file (multipart/form-data)
    - Requires authentication
    
    Returns:
        PDFUploadResponse with file information
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file selected"
            )
        
        if not allowed_file(file.filename, settings.allowed_extensions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        # Check file size
        file_content = await file.read()
        file_length = len(file_content)
        
        if file_length > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {settings.max_file_size} bytes"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Get user info
        user_uid = user['uid']
        
        # Upload to Firebase Storage
        storage_service = FirebaseStorageService()
        upload_result = storage_service.upload_file(
            file.file,
            user_uid,
            file.filename
        )
        
        # Get file size from Firebase Storage
        file_size = storage_service.get_file_size(upload_result['storage_path'])
        
        # Save metadata to Firestore
        db = firestore.client()
        file_id = upload_result['file_id']
        pdf_ref = db.collection('users').document(user_uid).collection('pdfs').document(file_id)
        
        pdf_data = {
            'file_id': file_id,
            'original_filename': upload_result['original_filename'],
            'unique_filename': upload_result['unique_filename'],
            'storage_path': upload_result['storage_path'],
            'size': file_size,
            'user_id': user_uid,
            'uploaded_at': firestore.SERVER_TIMESTAMP,
            'status': 'uploaded'
        }
        
        pdf_ref.set(pdf_data)
        
        # Construct file URL
        file_url = f"/api/pdf/{file_id}/download"
        
        return PDFUploadResponse(
            success=True,
            file_id=file_id,
            original_filename=upload_result['original_filename'],
            file_url=file_url,
            uploaded_at=datetime.utcnow(),
            size=file_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/{file_id}/download")
async def download_pdf(
    file_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Download PDF file from Firebase Storage
    Returns a signed URL that redirects to the file
    
    - **file_id**: UUID of the file
    - Requires authentication
    
    Returns:
        Redirect to signed URL (1-hour expiration)
    """
    try:
        user_uid = user['uid']
        
        # Get file metadata from Firestore
        db = firestore.client()
        pdf_ref = db.collection('users').document(user_uid).collection('pdfs').document(file_id)
        pdf_doc = pdf_ref.get()
        
        if not pdf_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        pdf_data = pdf_doc.to_dict()
        
        # Verify ownership
        if pdf_data.get('user_id') != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized"
            )
        
        # Generate signed URL from Firebase Storage
        storage_service = FirebaseStorageService()
        signed_url = storage_service.get_download_url(
            pdf_data['storage_path'],
            expiration=timedelta(hours=1)
        )
        
        # Redirect to signed URL
        return RedirectResponse(url=signed_url)
        
    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in storage"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}"
        )


@router.get("/list", response_model=PDFListResponse)
async def list_pdfs(user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all PDFs for current user
    
    - Requires authentication
    
    Returns:
        PDFListResponse with list of PDFs
    """
    try:
        user_uid = user['uid']
        
        # Get all PDFs for user
        db = firestore.client()
        pdfs_ref = db.collection('users').document(user_uid).collection('pdfs')
        pdfs = pdfs_ref.order_by('uploaded_at', direction=firestore.Query.DESCENDING).stream()
        
        pdf_list = []
        for pdf in pdfs:
            pdf_data = pdf.to_dict()
            pdf_list.append(PDFInfo(
                file_id=pdf_data['file_id'],
                original_filename=pdf_data['original_filename'],
                file_url=f"/api/pdf/{pdf_data['file_id']}/download",
                size=pdf_data['size'],
                uploaded_at=pdf_data.get('uploaded_at', datetime.utcnow()),
                status=pdf_data.get('status', 'uploaded')
            ))
        
        return PDFListResponse(
            success=True,
            pdfs=pdf_list,
            count=len(pdf_list)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list PDFs: {str(e)}"
        )


@router.delete("/{file_id}", response_model=SuccessResponse)
async def delete_pdf(
    file_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete PDF file from Firebase Storage and Firestore
    
    - **file_id**: UUID of the file
    - Requires authentication
    
    Returns:
        SuccessResponse
    """
    try:
        user_uid = user['uid']
        
        # Get file metadata from Firestore
        db = firestore.client()
        pdf_ref = db.collection('users').document(user_uid).collection('pdfs').document(file_id)
        pdf_doc = pdf_ref.get()
        
        if not pdf_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        pdf_data = pdf_doc.to_dict()
        
        # Verify ownership
        if pdf_data.get('user_id') != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized"
            )
        
        # Delete file from Firebase Storage
        storage_service = FirebaseStorageService()
        storage_service.delete_file(pdf_data['storage_path'])
        
        # Delete metadata from Firestore
        pdf_ref.delete()
        
        return SuccessResponse(
            success=True,
            message="File deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )
