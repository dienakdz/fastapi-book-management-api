from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app import models
from app.schemas.author import Author, AuthorCreate, AuthorUpdate

router = APIRouter()


@router.get("/", response_model=List[Author])
def list_authors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list authors, paginate sample use skip/limit
    """
    authors = db.query(models.Author).offset(skip).limit(limit).all()
    return authors

@router.get("/{author_id}", response_model=Author)
def get_author(
    author_id: int,
    db: Session = Depends(get_db)
    ):
    """Get author detail according id"""
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )
    
    return author

@router.post("/", response_model=Author, status_code=status.HTTP_201_CREATED)
def create_author(
    author_in: AuthorCreate,
    db: Session = Depends(get_db)
    ):
    """Create new author. Check unique name"""
    existing = db.query(models.Author).filter(models.Author.name == author_in.name).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author with this name already exists",
        )
    
    author = models.Author(name = author_in.name, bio = author_in.bio)
    db.add(author)
    db.commit()
    db.refresh(author)
    return author

@router.put("/{author_id}", response_model=Author)
def update_author(
    author_id: int,
    author_up: AuthorUpdate,
    db: Session = Depends(get_db)
    ):
    """Update author"""
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="author not found",
        )
    
    if author_up.name is not None and author_up.name != author.name:
        existing = db.query(models.Author).filter(models.Author.name == author_up.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another author with this name already exists",
            )
        author.name = author_up.name

    if author_up.bio is not None:
        author.bio = author_up.bio
    
    db.add(author)
    db.commit()
    db.refresh(author)
    return author

@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_author(
    author_id: int,
    db: Session = Depends(get_db)
    ):
    """Update author"""
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )
    
    db.delete(author)
    db.commit()