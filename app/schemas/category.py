from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    description: str | None = None

class CategoryCreate(CategoryBase):
    """Schema for create category"""
    pass

class CategoryUpdate(BaseModel):
    """Schema for update category"""
    name: str | None = None
    description: str | None = None

class CategoryInDBBase(CategoryBase):
    id: int

    class Config:
        from_attributes = True #Pydantic read from SQLAlchemy model

class Category(CategoryInDBBase):
    """Schema return for client"""
    pass