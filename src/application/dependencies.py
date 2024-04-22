from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.database import yield_async_session

AsyncDBSessionDepends = Annotated[AsyncSession, Depends(yield_async_session)]
