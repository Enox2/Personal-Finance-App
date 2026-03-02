from fastapi import APIRouter

from src.domains.auth.router import router as auth_router
from src.domains.csv.router import router as csv_router
from src.domains.etl.router import router as etl_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(csv_router)
api_router.include_router(etl_router)

