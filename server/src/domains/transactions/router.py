from fastapi import APIRouter, Depends

from src.domains.auth.dependencies import get_current_user
from src.domains.transactions.dependencies import get_transactions_service
from src.domains.transactions.schemas import TransactionRead
from src.domains.transactions.service import TransactionsService

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/uncategorised", response_model=list[TransactionRead])
async def list_uncategorised(
    limit: int = 100,
    service: TransactionsService = Depends(get_transactions_service),
):
    return await service.list_uncategorised(limit=limit)

