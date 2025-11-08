"""
PDF routes (file upload and management) - Subject-based structure
"""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Path

from app.dependencies.auth import get_current_user
from app.dependencies.service import get_pdf_service
from app.services.pdf_service import PDFService
from app.models.responses import PDFUploadResponse, PDFListResponse, PDFInfo, SuccessResponse

router = APIRouter(tags=["pdf"])


@router.post("/subjects/{subject_id}/pdfs/upload", response_model=PDFUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    subject_id: str = Path(..., description="Subject ID"),
    file: UploadFile = File(..., description="PDF file to upload"),
    user: Dict[str, Any] = Depends(get_current_user),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """
    Upload PDF file to Firebase Storage under a specific subject
    
    - **subject_id**: Subject ID
    - **file**: PDF file (multipart/form-data)
    - Requires authentication
    
    Returns:
        PDFUploadResponse with file information
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file selected"
        )
    
    # Read file content
    file_content = await file.read()
    file_length = len(file_content)
    
    # Reset file pointer
    await file.seek(0)
    
    # Upload using service
    result = pdf_service.upload_pdf(
        user['uid'],
        subject_id,
        file.file,
        file.filename,
        file_length
    )
    
    return PDFUploadResponse(
        success=True,
        file_id=result['file_id'],
        original_filename=result['original_filename'],
        file_url=result['file_url'],
        uploaded_at=result.get('uploaded_at', datetime.utcnow()),
        size=result['size']
    )


@router.get("/subjects/{subject_id}/pdfs/{file_id}/download")
async def download_pdf(
    subject_id: str = Path(..., description="Subject ID"),
    file_id: str = Path(..., description="File ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """
    Download PDF file from Firebase Storage
    Returns a JSON response with signed URL
    
    - **subject_id**: Subject ID
    - **file_id**: UUID of the file
    - Requires authentication
    
    Returns:
        JSON with download_url (1-hour expiration)
    """
    result = pdf_service.get_download_url(user['uid'], subject_id, file_id)
    return {
        "success": True,
        "download_url": result['download_url'],
        "filename": result['filename']
    }


@router.get("/subjects/{subject_id}/pdfs", response_model=PDFListResponse)
async def list_pdfs(
    subject_id: str = Path(..., description="Subject ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """
    List all PDFs for a specific subject
    
    - **subject_id**: Subject ID
    - Requires authentication
    
    Returns:
        PDFListResponse with list of PDFs
    """
    pdfs = pdf_service.list_pdfs(user['uid'], subject_id)
    
    pdf_list = [
        PDFInfo(
            file_id=pdf.file_id,
            original_filename=pdf.original_filename,
            file_url=f"/api/subjects/{subject_id}/pdfs/{pdf.file_id}/download",
            size=pdf.size,
            uploaded_at=pdf.uploaded_at,
            status=pdf.status
        )
        for pdf in pdfs
    ]
    
    return PDFListResponse(
        success=True,
        pdfs=pdf_list,
        count=len(pdf_list)
    )


@router.delete("/subjects/{subject_id}/pdfs/{file_id}", response_model=SuccessResponse)
async def delete_pdf(
    subject_id: str = Path(..., description="Subject ID"),
    file_id: str = Path(..., description="File ID"),
    user: Dict[str, Any] = Depends(get_current_user),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """
    Delete PDF file from Firebase Storage and Firestore
    
    - **subject_id**: Subject ID
    - **file_id**: UUID of the file
    - Requires authentication
    
    Returns:
        SuccessResponse
    """
    pdf_service.delete_pdf(user['uid'], subject_id, file_id)
    return SuccessResponse(
        success=True,
        message="File deleted successfully"
    )
