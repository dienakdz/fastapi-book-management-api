# Book Management API (FastAPI)

FastAPI project to manage **Authors**, **Categories**, **Books**, plus cover image uploads stored under static files. Ships with SQLite by default and Alembic migrations.

## Stack
- Python 3.11+ (tested on 3.12)
- FastAPI + Uvicorn
- SQLAlchemy ORM
- Alembic (migrations)
- Pydantic v2
- python-multipart (file upload)
- SQLite by default (can switch to PostgreSQL/MySQL)

## Project structure
- `app/main.py`: FastAPI app bootstrap, mounts `/static`, includes routers.
- `app/api/endpoints/`: REST endpoints for authors, categories, books, cover upload.
- `app/api/deps.py`: DB session dependency.
- `app/models/`: SQLAlchemy models.
- `app/schemas/`: Pydantic schemas for request/response.
- `app/core/config.py`: Basic config, DB URL.
- `app/db/`: Engine, session, Base.
- `app/static/covers/`: Uploaded cover images.
- `migrations/`: Alembic config and revisions.

## Setup
```bash
# 1) Create & activate virtualenv
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 2) Install dependencies
pip install -U pip
pip install fastapi uvicorn[standard] sqlalchemy alembic pydantic python-multipart
```

## Database config
- Default: SQLite file `app.db` via `sqlite:///./app.db` in `app/core/config.py`.
- To use another DB, update `SQLALCHEMY_DATABASE_URI` in `app/core/config.py` and match `sqlalchemy.url` in `alembic.ini` (example PostgreSQL: `postgresql+psycopg2://user:pass@localhost:5432/books`).

## Migrations
```bash
# Apply latest schema
alembic upgrade head

# Create new migration after editing models
# Ensure models are imported into metadata (see note below)
alembic revision --autogenerate -m "describe changes"
alembic upgrade head
```
**Note:** If autogenerate cannot see tables, open `app/db/base.py` and import Author, Category, Book so Alembic can read the metadata.

## Run the app
```bash
uvicorn app.main:app --reload
# App will be at http://127.0.0.1:8000
```
- Swagger UI: `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`
- Static covers: `http://127.0.0.1:8000/static/covers/...`

## Key endpoints
### Authors (`/authors`)
- `GET /authors?skip=0&limit=100`
- `GET /authors/{author_id}`
- `POST /authors` body:
  ```json
  { "name": "George Orwell", "bio": "Author of 1984" }
  ```
- `PUT /authors/{author_id}` (name uniqueness check)
- `DELETE /authors/{author_id}`

### Categories (`/categories`)
- `GET /categories?skip=0&limit=100`
- `GET /categories/{category_id}`
- `POST /categories` body:
  ```json
  { "name": "Science Fiction", "description": "Futuristic narratives" }
  ```
- `PUT /categories/{category_id}`
- `DELETE /categories/{category_id}`

### Books (`/books`)
- `GET /books?skip=0&limit=100&author_id=&category_id=&year=&keyword=` (filter by author, category, year, keyword on title/description)
- `GET /books/{book_id}`
- `POST /books` body (needs valid author/category ids):
  ```json
  {
    "title": "1984",
    "description": "Dystopian novel",
    "published_year": 1949,
    "author_id": 1,
    "category_id": 1
  }
  ```
- `PUT /books/{book_id}` (validates author/category on change)
- `DELETE /books/{book_id}`

### Upload cover (`/books/{book_id}/cover`)
- Send `multipart/form-data` with field `file`.
- Accepts `jpg`, `jpeg`, `png`; ~2MB max.
- Stored under `app/static/covers/`; returns URL `/static/covers/<filename>`.
```bash
curl -X POST http://127.0.0.1:8000/books/1/cover \
  -F "file=@/path/to/cover.jpg"
```

## Quick test (sample cURL)
```bash
# Create author
curl -X POST http://127.0.0.1:8000/authors \
  -H "Content-Type: application/json" \
  -d '{"name":"George Orwell","bio":"Author of 1984"}'

# Create category
curl -X POST http://127.0.0.1:8000/categories \
  -H "Content-Type: application/json" \
  -d '{"name":"Science Fiction","description":"Futuristic"}'

# Create book
curl -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"1984","description":"Dystopia","published_year":1949,"author_id":1,"category_id":1}'
```

## Production tips
- Run multiple workers: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`
- Put Nginx/Apache in front to serve `/static`.
- Configure production DB via env vars or by editing `app/core/config.py` and `alembic.ini`.

## YouTube video
Watch here: [my link](https://www.youtube.com/@dienne248)
