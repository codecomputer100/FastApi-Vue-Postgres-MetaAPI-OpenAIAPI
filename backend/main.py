# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from settings import settings
from auth import router as auth_router
from meta_api import router as meta_router

app = FastAPI(title="Meta Campaign Viewer API")

# CORS: importante allow_credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],  # ej: "http://localhost:5173"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(meta_router)

@app.get("/")
def home():
    return {"message": "Backend activo ✅"}
