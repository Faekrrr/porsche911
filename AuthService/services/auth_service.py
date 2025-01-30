from models.user import User as UserModel, UserCreate
from sqlalchemy.orm import Session
from utils.hashing import Hash
from utils.jwt import create_access_token

class AuthService:
    @staticmethod
    async def register_user(user: UserCreate, db: Session):
        hashed_password = Hash.bcrypt(user.password)
        db_user = UserModel(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    async def authenticate_user(username: str, password: str, db: Session):
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if not user or not Hash.verify(user.hashed_password, password):
            return None
        return create_access_token(data={"sub": user.username})