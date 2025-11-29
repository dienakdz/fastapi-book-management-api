from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api.deps import get_db
from app import models
from app.schemas.book import Book, BookCreate, BookUpdate
from pathlib import Path
import uuid

router = APIRouter()

# Folder save cover image
COVERS_DIR = Path("app/static/covers")
COVERS_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/", response_model=List[Book])
def list_books(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    author_id: int | None = Query(None),
    category_id: int | None = Query(None),
    year: int | None = Query(None),
    keyword: str | None = Query(None),
):
    
    """
    Get list books, include filter:
    
    - author_id
    - category_id
    - year (published_year)
    - keyword (search in title or desc)
    """
    mb = models.Book
    query = db.query(mb)
    if author_id is not None:
        query = query.filter(mb.author_id == author_id)
    if category_id is not None:
        query = query.filter(mb.category_id == category_id)

    if year is not None:
        query = query.filter(mb.published_year == year)

    if keyword is not None:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                mb.title.ilike(like_pattern),
                mb.description.ilike(like_pattern),
            )
        )
    
    books = query.offset(skip).limit(limit).all()
    return books


@router.get("/{book_id}", response_model=Book)
def get_book(
    book_id: int,
    db: Session = Depends(get_db)
    ):
    """Get book detail according id"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    return book

@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db)
    ):
    author = db.query(models.Author).filter(models.Author.id == book_in.author_id).first()

    if not author:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author does not exist",
        )
    
    category = db.query(models.Category).filter(models.Category.id == book_in.category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category does not exist",
        )
    
    book = models.Book(
        title = book_in.title,
        description = book_in.description,
        published_year = book_in.published_year,
        author_id = book_in.author_id,
        category_id = book_in.category_id,
        )
    
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.put("/{book_id}", response_model=Book)
def update_book(
    book_id: int,
    book_up: BookUpdate,
    db: Session = Depends(get_db)
    ):
    """
    Update book
    - Allow update author_id/ category_id, but must check exists
    """
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    if book_up.title is not None:
        book.title = book_up.title
    if book_up.description is not None:
        book.description = book_up.description
    if book_up.published_year is not None:
        book.published_year = book_up.published_year

    # if update author_id
    if book_up.author_id is not None and book_up.author_id != book.author_id:
        author = db.query(models.Author).filter(models.Author.id == book_up.author_id).first()
        if not author:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New author does not exist",
            )
        book.author_id = book_up.author_id

    # if update author_id
    if book_up.category_id is not None and book_up.category_id != book.category_id:
        category = db.query(models.Category).filter(models.Category.id == book_up.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New category does not exist",
            )
        book.category_id = book_up.category_id
    
    
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_book(
    book_id: int,
    db: Session = Depends(get_db)
    ):
    """Delete book"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    db.delete(book)
    db.commit()

@router.post("/{book_id}/cover", response_model=Book)
async def upload_book_cover(
    book_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload cover image for book
    
    - Allow jpg/png/jpeg
    - Save file in path : app/static/covers
    - Update book.cover_image to URL /static/covers/...
    """
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    # Validate content type
    if file.content_type not in ['image/jpeg', "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image type. Only JPEG and PNG are allowed.",
        )
    
    # Get extension of file
    ext = Path(file.filename).suffix.lower()
    if ext not in ['.jpeg', ".png", ".jpg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image type. Only .jpg, .jpeg, .png are allowed.",
        )
    
    # Read content file
    contents = await file.read()

    #Optional, limit size 2MB
    max_size = 2 * 1024 * 1024 #2MB
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File to large. Max size is 2MB",
        )
    
    # Generate file name
    filename = f"book_{book_id}_{uuid.uuid4().hex}{ext}"
    file_path = COVERS_DIR / filename

    # Write to disk
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Update url cover_image
    book.cover_image = f"/static/covers/{filename}"

    db.add(book)
    db.commit()
    db.refresh

    return book
