from typing import Optional, List

import databases
import sqlalchemy
import ormar
from app.core.config import settings


database = databases.Database(settings.DATABASE_URI)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(settings.DATABASE_URI)


class User(ormar.Model):
    class Meta:
        database = database
        metadata = metadata

    id: int = ormar.Integer(primary_key=True)
    username: str = ormar.String(max_length=100, unique=True)
    active: bool = ormar.Boolean(default=True)
    hashed_password: str = ormar.String(max_length=64)


metadata.create_all(engine)

