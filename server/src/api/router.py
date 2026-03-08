from fastapi import APIRouter

from src.domains.auth.router import router as auth_router
from src.domains.csv.router import router as csv_router
from src.domains.processing.router import router as processing_router
from src.domains.rules.router import router as rules_router
from src.domains.transactions.router import router as transactions_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(csv_router)
api_router.include_router(rules_router)
api_router.include_router(transactions_router)
api_router.include_router(processing_router)
