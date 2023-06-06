import os
from typing import List
from uuid import UUID

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic.main import BaseModel
from starlette import status

from crud.audio import CRUDAudio
from depedences.common import RequiredRoles, get_raw_token
from errors import ForbiddenError
from models.client import DBUser, EditableUserBase, User, UserBase, UserRole
from models.token import TokenData, TokensResp, TokenType
from schemas.schema import (
    AudioSchemaReq,
    CreateUserReq,
    LoginByEmailReq,
    UpdateUserAdminReq,
    UpdateUserReq,
)
from utils.jwt_service import jwt_service

load_dotenv(".env")

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = os.environ["ALGORITHM"]
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_REFRESH_SECRET_KEY = os.environ["JWT_REFRESH_SECRET_KEY"]

ROUTER = APIRouter(prefix="/auth", tags=["User"])

from crud.user import CRUDUser
from depedences.cruds import get_audio_crud, get_users_crud


@ROUTER.post(
    "/create",
    status_code=status.HTTP_200_OK,
    summary="Create user",
)
async def create_user(
    new_user: CreateUserReq,
    user_crud: CRUDUser = Depends(get_users_crud)
    # token: TokenData = Depends(
    #     RequiredRoles(
    #         [
    #             UserRole.admin,
    #             UserRole.user
    #         ]
    #     )
    # )
):
    if await user_crud.check_email_user_exists(email=new_user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same email",
        )
    user = await user_crud.create_user(obj_in=new_user)
    return user


@ROUTER.post(
    "/login",
    summary="Login by credentials to get token",
    response_model=TokensResp,
)
async def login_by_email(
    req: LoginByEmailReq, user_crud: CRUDUser = Depends(get_users_crud)
):
    """
    API method to authorize by email and password.
    Return pairs of access and refresh tokens.

    :param req: email and password data
    :type req: LoginByEmailReq
    :param user_crud: CRUD wrapper
    :type user_crud: CRUDUser
    """

    user = await user_crud.authenticate(email=req.email, password=req.password)
    access_token = jwt_service.create_access_token(user.id, user.role)
    refresh_token = jwt_service.create_refresh_token(user.id, user.role)
    return TokensResp(
        access_token=access_token,
        refresh_token=refresh_token,
    )


class RefreshTokenReq(BaseModel):
    """
    Model containing refresh token data.
    """

    token: str


@ROUTER.post(
    "/auth/refresh",
    status_code=status.HTTP_200_OK,
    summary="Refresh token",
    description="Returns a new pair of access and "
    "refresh tokens if refresh token is valid",
    response_model=TokensResp,
)
async def refresh(
    req: RefreshTokenReq,
    token: TokenData = Depends(RequiredRoles([UserRole.admin, UserRole.user])),
):
    """
    API method to refresh access and refresh tokens by provided refresh token.

    :param req: refresh token data
    :type req: RefreshTokenReq
    """
    old_token = jwt_service.decode_token(req.token)
    if old_token.type != TokenType.refresh:
        raise ForbiddenError()
    access_token = jwt_service.create_access_token(old_token.user_id, old_token.role)
    refresh_token = jwt_service.create_refresh_token(old_token.user_id, old_token.role)
    return TokensResp(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@ROUTER.put(
    "/update_current_user",
    status_code=status.HTTP_200_OK,
    summary="Update current user",
    response_model=User,
)
async def edit_current_user(
    update_user_data: UpdateUserReq,
    token: TokenData = Depends(
        RequiredRoles(
            [
                UserRole.admin,
                UserRole.manager,
                UserRole.user,
            ]
        )
    ),
    user_crud: CRUDUser = Depends(get_users_crud),
):
    user = await user_crud.update(obj_id=token.user_id, obj_new=update_user_data)
    return user
