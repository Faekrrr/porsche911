from fastapi import FastAPI
from routes.user import user_router
from database import engine, Base

app = FastAPI()

app.include_router(user_router)

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "UserService is running"}
