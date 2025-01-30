from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    profile_picture = Column(String, nullable=True)
    background_picture = Column(String, nullable=True)
    description = Column(String, nullable=True)
    skills = Column(JSON, nullable=True)
    experience = Column(JSON, nullable=True)
    certifications = Column(JSON, nullable=True)
    availability = Column(String, nullable=True)

    def __repr__(self):
        return f"<User(username={self.username}, created_at={self.created_at})>"
