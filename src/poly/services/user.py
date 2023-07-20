from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from poly.db.models import User


async def get_user(email: str, session: AsyncSession) -> User | None:
    query = select(User).where(User.email == email)
    result = await session.scalars(query)
    return result.one_or_none()
