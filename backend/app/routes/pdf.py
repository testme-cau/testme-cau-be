"""
PDF routes (file upload and management) - Subject-based structure
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Path
from fastapi.responses import RedirectResponse
from firebase_admin import firestore

from app.dependencies.auth import get_current_user
from app.services.firebase_storage import FirebaseStorageService
from app.utils.file_utils import allowed_file
from app.models.responses import PDFUploadResponse, PDFListResponse, PDFInfo, SuccessResponse
from config import settings

router = APIRouter(tags=["pdf"])


@router.post("/subjects/{subject_id}/pdfs/upload", response_model=PDFUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    subject_id: str = Path(..., description="Subject ID"),
    file: UploadFile = File(..., description="PDF file to upload"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload PDF file to Firebase Storage under a specific subject
    
    - **subject_id**: Subject ID
    - **file**: PDF file (multipart/form-data)
    - Requires authentication
    
    Returns:
        PDFUploadResponse with file information
    """
    try:
        user_uid = user['uid']
        
        # Verify subject exists and belongs to user
        db = firestore.client()
        subject_ref = db.collection('users').document(user_uid).collection('subjects').document(subject_id)
        subject_doc = subject_ref.get()
        
        if not subject_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        subject_data = subject_doc.to_dict()
        if subject_data.get('user_id') != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized"
            )
        
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
        
        # Upload to Firebase Storage
        storage_service = FirebaseStorageService()
        upload_result = storage_service.upload_file(
            file.file,
            user_uid,
            file.filename
        )
        
        # Get file size from Firebase Storage
        file_size = storage_service.get_file_size(upload_result['storage_path'])
        
        # Save metadata to Firestore under subject
        file_id = upload_result['file_id']
        pdf_ref = subject_ref.collection('pdfs').document(file_id)
        
        pdf_data = {
            'file_id': file_id,
            'subject_id': subject_id,
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
        file_url = f"/api/subjects/{subject_id}/pdfs/{file_id}/download"
        
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


@router.get("/subjects/{subject_id}/pdfs/{file_id}/download")
async def download_pdf(
    subject_id: str = Path(..., description="Subject ID"),
    file_id: str = Path(..., description="File ID"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Download PDF file from Firebase Storage
    Returns a signed URL that redirects to the file
    
    - **subject_id**: Subject ID
    - **file_id**: UUID of the file
    - Requires authentication
    
    Returns:
        Redirect to signed URL (1-hour expiration)
    """
    try:
        user_uid = user['uid']
        
        # Get file metadata from Firestore
        db = firestore.client()
        subject_ref = db.collection('users').document(user_uid).collection('subjects').document(subject_id)
        pdf_ref = subject_ref.collection('pdfs').document(file_id)
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


@router.get("/subjects/{subject_id}/pdfs", response_model=PDFListResponse)
async def list_pdfs(
    subject_id: str = Path(..., description="Subject ID"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List all PDFs for a specific subject
    
    - **subject_id**: Subject ID
    - Requires authentication
    
    Returns:
        PDFListResponse with list of PDFs
    """
    try:
        user_uid = user['uid']
        
        # Verify subject exists
        db = firestore.client()
        subject_ref = db.collection('users').document(user_uid).collection('subjects').document(subject_id)
        subject_doc = subject_ref.get()
        
        if not subject_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Get all PDFs for subject
        pdfs_ref = subject_ref.collection('pdfs')
        pdfs = pdfs_ref.order_by('uploaded_at', direction=firestore.Query.DESCENDING).stream()
        
        pdf_list = []
        for pdf in pdfs:
            pdf_data = pdf.to_dict()
            pdf_list.append(PDFInfo(
                file_id=pdf_data['file_id'],
                original_filename=pdf_data['original_filename'],
                file_url=f"/api/subjects/{subject_id}/pdfs/{pdf_data['file_id']}/download",
                size=pdf_data['size'],
                uploaded_at=pdf_data.get('uploaded_at', datetime.utcnow()),
                status=pdf_data.get('status', 'uploaded')
            ))
        
        return PDFListResponse(
            success=True,
            pdfs=pdf_list,
            count=len(pdf_list)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list PDFs: {str(e)}"
        )


@router.delete("/subjects/{subject_id}/pdfs/{file_id}", response_model=SuccessResponse)
async def delete_pdf(
    subject_id: str = Path(..., description="Subject ID"),
    file_id: str = Path(..., description="File ID"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete PDF file from Firebase Storage and Firestore
    
    - **subject_id**: Subject ID
    - **file_id**: UUID of the file
    - Requires authentication
    
    Returns:
        SuccessResponse
    """
    try:
        user_uid = user['uid']
        
        # Get file metadata from Firestore
        db = firestore.client()
        subject_ref = db.collection('users').document(user_uid).collection('subjects').document(subject_id)
        pdf_ref = subject_ref.collection('pdfs').document(file_id)
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
