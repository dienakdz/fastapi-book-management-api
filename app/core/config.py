from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Book Management API"
    
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./app.db"

settings = Settings()