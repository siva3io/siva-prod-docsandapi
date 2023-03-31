from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_ipaddr
from starlette.middleware.authentication import AuthenticationMiddleware
from app.jwt import JWTAuthenticationBackend

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_application():

    _app = FastAPI(
        title=settings.PROJECT_NAME,
        description="An API providing end points to use Advanced Data Science models that we have developed",
        version=settings.PROJECT_VERSION,
        terms_of_service="http://eunimart.com/terms/",
        contact={
            "name": "Eunimart",
            "url": "https://eunimart.com/",
            "email": "contact@eunimart.com",
        },
        openapi_url="/api/v1/openapi.json",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1}
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.add_middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend(
        secret_key=settings.SECRET_KEY, prefix="Bearer"
    ))

    return _app


def get_limiter():
    limiter = Limiter(key_func=get_ipaddr)
    return limiter
