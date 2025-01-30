from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import User
from database import SessionLocal
from utils.jwt import create_access_token, create_refresh_token, verify_refresh_token
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    profile_picture: Optional[HttpUrl] = None
    background_picture: Optional[HttpUrl] = None
    description: Optional[str] = None
    skills: Optional[list[dict]] = []
    experience: Optional[list[dict]] = []
    certifications: Optional[list[str]] = []
    availability: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    profile_picture: Optional[HttpUrl]
    background_picture: Optional[HttpUrl]
    description: Optional[str]
    skills: Optional[list[dict]]
    experience: Optional[list[dict]]
    certifications: Optional[list[str]]
    availability: Optional[str]

    class Config:
        orm_mode = True
        
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        username=user.username,
        hashed_password=user.password,
        email=user.email,
        profile_picture=user.profile_picture,
        background_picture=user.background_picture,
        description=user.description,
        skills=user.skills,
        experience=user.experience,
        certifications=user.certifications,
        availability=user.availability
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
async def login_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_request: RefreshTokenRequest):
    username = verify_refresh_token(refresh_request.refresh_token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token(data={"sub": username})
    refresh_token = create_refresh_token(data={"sub": username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}