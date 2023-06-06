"""
This module contains CRUDs dependencies which create separate database session
for current user and gives access to database operations.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from async_db import get_async_session
from crud.audio import CRUDAudio
from crud.user import CRUDUser

# from crud.token import CRUDToken
from models.client import DBAudio, DBUser


async def get_users_crud(
    session: AsyncSession = Depends(get_async_session),
) -> CRUDUser:
    """
    Dependency Injection method to get User CRUD wrapper for current session.

    :param session: active user HTTP session
    :type session: AsyncSession
    :return: User CRUD
    :rtype: CRUDUser
    """
    return CRUDUser(DBUser, session=session)


async def get_audio_crud(
    session: AsyncSession = Depends(get_async_session),
) -> CRUDAudio:
    """
    Dependency Injection method to get Audio CRUD wrapper for current session.
    """
    return CRUDAudio(DBAudio, session=session)
