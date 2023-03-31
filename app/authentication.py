from datetime import timedelta, datetime

from fastapi import Depends, HTTPException, status, APIRouter, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from starlette.authentication import AuthenticationError
from asyncpg.exceptions import UniqueViolationError
from ormar.exceptions import NoMatch
from typing import Optional

from app.core.schemas import Token
from app.core.config import settings
from app.database import User


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(username, password):
    try:
        user = await User.objects.get(username=username)
    except NoMatch as exe:
        raise AuthenticationError("Username or password is incorrect!")
    verified = pwd_context.verify(password, user.hashed_password)
    if not verified:
        raise AuthenticationError("Username or password is incorrect!")
    return user


def get_access_token(data):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": data}, expires_delta=access_token_expires
    )
    return access_token


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = get_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/user", response_model=Token)
async def create_user(username: str = Body(), password: str = Body()):
    hashed_password = pwd_context.hash(password)
    try:
        user = await User.objects.create(username=username, hashed_password=hashed_password)
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the given username already exists!"
        )
    access_token = get_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}
