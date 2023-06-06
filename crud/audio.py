"""
Module that contains User CRUD subclass. Contains custom logic to handle
user retrieval, creation and authentication.
"""
from typing import List, Optional
from urllib.request import Request
from uuid import UUID

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import select
from starlette import status

from crud.base import CRUDBase, ModelType
from models.client import DBAudio
from routers.security import get_password_hash, verify_password
from schemas.schema import AudioLink, AudioSchema, AudioSchemaReq


class CRUDAudio(CRUDBase[DBAudio, AudioSchemaReq, AudioSchema]):
    async def create_audio(self, *, obj_in: AudioSchemaReq) -> DBAudio:
        """
        Method to create audios.
        """
        db_obj = DBAudio.from_orm(obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_links_from_db(self, user_id):
        """
        Method to get audios by user_id.
        """
        user = await self.session.execute(
            select(DBAudio).where(DBAudio.user_id == user_id)
        )
        audios = user.scalars().all()
        all_links = []
        for i in audios:
            all_links.append(i.link)
        return all_links

    async def get_audio_info(
        self,
    ):
        """
        Method to get all audios.
        """
        user = await self.session.execute(select(DBAudio))
        audios = user.scalars().all()
        return audios

    async def del_from_db(self, record_id: UUID):
        response = await self.session.execute(
            select(DBAudio).where(DBAudio.id == record_id)
        )
        """
        Method to delete audios from db by record id.
        """
        obj = response.scalars().all()
        if obj:
            for i in obj:
                await self.session.delete(i)
                await self.session.commit()
        return obj

    async def user_del_audio_from_db(self, record_id: UUID, user_id: UUID):
        response = await self.session.execute(
            select(DBAudio)
            .where(DBAudio.user_id == user_id)
            .where(DBAudio.id == record_id)
        )
        """
        Method to delete own audios.
        """
        obj = response.scalars().all()
        if obj:
            for i in obj:
                await self.session.delete(i)
                await self.session.commit()
        return obj

    async def get_record_title(self, record_id: UUID) -> AudioSchema:
        """
        Method to get audio by record id.
        """
        query = await self.session.execute(
            select(DBAudio).where(DBAudio.id == record_id)
        )
        return query.scalar_one_or_none()

    async def get_by_user_id_record_id(
        self, user_id: UUID, record_id: UUID
    ) -> AudioSchema:
        """
        Method to get audio by user id and record id.
        """
        query = await self.session.execute(
            select(DBAudio)
            .where(DBAudio.id == record_id)
            .where(DBAudio.user_id == user_id)
        )
        return query.scalar_one_or_none()
