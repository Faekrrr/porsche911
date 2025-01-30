from sqlalchemy import Column, Integer, String, JSON, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from database import Base
from typing import Optional, List

portfolio_collaborators = Table(
    "portfolio_collaborators",
    Base.metadata,
    Column("portfolio_id", Integer, ForeignKey("portfolios.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    profile_picture = Column(String, nullable=True)
    background_picture = Column(String, nullable=True)
    description = Column(String, nullable=True)
    skills = Column(JSON, nullable=True)
    experience = Column(JSON, nullable=True)
    certifications = Column(JSON, nullable=True)
    availability = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    hashed_password = Column(String, nullable=True)

    portfolio_items = relationship("Portfolio", back_populates="user")
    stars = relationship("Star", back_populates="user")
    collaborations = relationship("Portfolio", secondary=portfolio_collaborators, back_populates="collaborators")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"

class Skill(BaseModel):
    name: str
    level: int

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    repo_link = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    star_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="portfolio_items")
    stars = relationship("Star", back_populates="portfolio")
    highlights = relationship("Highlight", back_populates="portfolio", cascade="all, delete-orphan")
    collaborators = relationship("User", secondary=portfolio_collaborators, back_populates="collaborations")

class PortfolioCreate(BaseModel):
    name: str
    repo_link: str
    description: str = None
    tags: list[str] = []
    collaborators: Optional[List[int]] = []  
    is_private: bool = False
    allowed_users: Optional[List[int]] = []

class Highlight(Base):
    __tablename__ = "highlights"

    id = Column(Integer, primary_key=True, index=True)
    media_url = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)

    portfolio = relationship("Portfolio", back_populates="highlights")

class HighlightCreate(BaseModel):
    media_url: str
    description: str = None
    tags: list[str] = []

class Star(Base):
    __tablename__ = "stars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="stars")
    portfolio = relationship("Portfolio", back_populates="stars")

class UserUpdate(BaseModel):
    username: str
    email: str
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    description: Optional[str] = None
    skills: list[dict] = []
    experience: list[dict] = []
    certifications: list[str] = []
    availability: Optional[str] = None

class Experience(BaseModel):
    employer: str
    position: str
    start_date: str
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[dict]] = []
    experience: Optional[List[dict]] = []
    certifications: Optional[List[str]] = []
    availability: Optional[str] = None

    class Config:
        orm_mode = True