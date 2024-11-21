from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .database import Base, engine
from .routers import books, categories,auth, users, downloads
from app.models import Base 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
Base.metadata.create_all(bind=engine)
# Create tables
# Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
allow_origins = ['http://localhost:8081',
                 'http://192.168.160.121:8081',
                 'http://192.168.254.184:8081','192.168.254.199:44970']

app.add_middleware(
    CORSMiddleware,
    allow_origins = allow_origins,
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","DELETE","PATCH"],
    allow_headers=["X-Requested-With","Content-Type"]
)

# Include routers
app.include_router(books.app)
app.include_router(categories.router)
app.include_router(auth.authRouth)
app.include_router(users.router)
app.include_router(downloads.router)

@app.get("/")
def read_root():
    return RedirectResponse('/docs')# {"message": "Welcome to digitalShelves API"}
