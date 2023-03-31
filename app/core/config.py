import os

from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_VERSION: float
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GOOGLE_SERVICE_ACCOUNT: str

    ELASTIC_SEARCH_URL: str
    ELASTIC_USERNAME: str
    ELASTIC_PASSWORD: str
    ELASTIC_INDEX: str

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_SERVER: str = None
    POSTGRES_USER: str = None
    POSTGRES_PASSWORD: str = None
    POSTGRES_DB: str = None
    DATABASE_URI: Optional[str] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        try:
            postgres_uri = PostgresDsn.build(
                scheme="postgresql",
                user=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=values.get("POSTGRES_SERVER"),
                path=f"/{values.get('POSTGRES_DB') or ''}",
            )
            return postgres_uri
        except Exception as exe:
            return "sqlite:///db.sqlite"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_SERVICE_ACCOUNT
# print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
