from sqlalchemy.orm import declarative_base

Base = declarative_base()

#Import models for Alembic can scan metadata
# from app.models.author import Author
# from app.models.category import Category
# from app.models.book import Book