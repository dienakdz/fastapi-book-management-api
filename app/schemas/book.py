from pydantic import BaseModel
from datetime import datetime

from app.schemas.author import Author
from app.schemas.category import Category

class BookBase(BaseModel):
    title: str
    description: str
    published_year: int
    category_id: int
    author_id: int

class BookCreate(BookBase):
    """Schema for create Book"""
    pass

class BookUpdate(BaseModel):
    """Schema for update Book"""
    title: str | None = None
    description: str | None = None
    published_year: int | None = None
    category_id: int | None = None
    author_id: int | None = None

class BookInDBBase(BookBase):
    id: int
    title: str
    description: str
    published_year: int
    category_id: int
    author_id: int
    cover_image: str | None = None
    created_at: datetime 
    updated_at: datetime

    class Config:
        from_attributes = True #Pydantic read from SQLAlchemy model

#Schema nested for author and category
class Book(BookInDBBase):
    author: Author
    category: Category