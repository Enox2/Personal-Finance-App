from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.csv.router import router as csv_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(csv_router)
