from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AccessToken, User
from src.auth.password import verify_password


async def authenticate(
    username: str, password: str, session: AsyncSession
) -> User | None:
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    user: User | None = result.scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def create_access_token(user: User, session: AsyncSession) -> AccessToken:
    access_token = AccessToken(user=user)
    session.add(access_token)
    await session.commit()
    return access_token
