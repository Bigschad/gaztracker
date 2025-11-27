"""
File Upload API Routes

Endpoints for uploading and serving files (logos, documents, etc.).
"""

import os
import shutil
from typing import List
from uuid import uuid4
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_sync_db
from app.models.user import User
from app.middleware.auth_middleware import get_current_user_sync
from app.config import settings

router = APIRouter()

# Allowed image extensions
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Upload directory
UPLOAD_DIR = Path("/app/uploads")
LOGOS_DIR = UPLOAD_DIR / "logos"

# Note: Directories are created in Dockerfile with proper permissions


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file."""
    # Check extension
    if file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Type de fichier non autorisé. Extensions autorisées: {', '.join(ALLOWED_EXTENSIONS)}"
            )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux. Taille maximale: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )


@router.post("/logos", status_code=status.HTTP_201_CREATED)
def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Upload a logo image.
    
    Returns the URL path to access the uploaded logo.
    
    - **file**: Image file (JPG, PNG, GIF, SVG, WEBP)
    - Max size: 5MB
    """
    try:
        # Validate file
        validate_image_file(file)
        
        # Generate unique filename
        ext = os.path.splitext(file.filename or "logo.png")[1].lower()
        filename = f"{uuid4()}{ext}"
        file_path = LOGOS_DIR / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return URL path
        url_path = f"/api/v1/uploads/logos/{filename}"
        
        return {
            "url": url_path,
            "filename": filename,
            "original_filename": file.filename,
            "size": os.path.getsize(file_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )
    finally:
        file.file.close()


@router.get("/logos/{filename}")
def get_logo(filename: str):
    """
    Serve a logo file.
    
    - **filename**: Name of the logo file to retrieve
    """
    file_path = LOGOS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logo non trouvé"
        )
    
    return FileResponse(file_path)


@router.delete("/logos/{filename}", status_code=status.HTTP_204_NO_CONTENT)
def delete_logo(
    filename: str,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Delete a logo file.
    
    Requires authentication.
    
    - **filename**: Name of the logo file to delete
    """
    file_path = LOGOS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logo non trouvé"
        )
    
    try:
        os.remove(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

