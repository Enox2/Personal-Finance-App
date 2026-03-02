from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.domains.auth import schemas
from src.domains.auth.authentication import authenticate, create_access_token
from src.domains.auth.dependencies import get_current_user
from src.domains.auth.models import User
from src.domains.auth.password import get_password_hash

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRead
)
async def register(
    user_create: schemas.UserCreate, session: AsyncSession = Depends(get_async_session)
) -> User:
    hashed_password = get_password_hash(user_create.password)
    user = User(
        **user_create.model_dump(exclude={"password"}), hashed_password=hashed_password
    )

    try:
        session.add(user)
        await session.commit()
    except exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    return user


@router.post("/token")
async def create_token(
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    session: AsyncSession = Depends(get_async_session),
):
    email = form_data.username
    password = form_data.password
    user = await authenticate(email, password, session)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = await create_access_token(user, session)

    return {"access_token": token.access_token, "token_type": "bearer"}


@router.get("/protected-route", response_model=schemas.UserRead)
async def protected_route(user: User = Depends(get_current_user)):
    return user

