from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import Category 
from app.schemas.category import CategoryResponse
from app.models import SessionLocal,Base

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)
# Route to get all categories
@router.get("/", response_model=list[CategoryResponse])
async def get_categories():
    db = SessionLocal()
    categories = db.query(Category).all()
    return categories