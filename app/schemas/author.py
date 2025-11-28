from pydantic import BaseModel

class AuthorBase(BaseModel):
    name: str
    bio: str | None = None

class AuthorCreate(AuthorBase):
    """Schema for create Author"""
    pass

class AuthorUpdate(BaseModel):
    """Schema for update Author"""
    name: str | None = None
    bio: str | None = None

class AuthorInDBBase(AuthorBase):
    id: int

    class Config:
        orm_mode = True #Pydantic read from SQLAlchemy model

class Author(AuthorInDBBase):
    """Schema return for client"""
    pass