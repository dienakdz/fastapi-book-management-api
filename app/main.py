from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import authors, categories, books
app = FastAPI(
    title="Book Management API",
    description="Simple API to manage books, authors, categories and book covers",
    version="1.0.0"
)

#Include routes
app.include_router(authors.router, prefix="/authors", tags=["Authors"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(books.router, prefix="/books", tags=["Books"])

#Static files for covers image

@app.get("/")
def read_root():
    return {"message": "Book management API is running"}