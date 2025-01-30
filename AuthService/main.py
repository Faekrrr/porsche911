from fastapi import FastAPI
from routes.auth import router
from database import engine, Base

app = FastAPI()

app.include_router(router)

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "AuthService is running"}
