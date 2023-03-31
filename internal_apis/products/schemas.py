from pydantic import BaseModel


class QueryResponse(BaseModel):
    query: str
    count: int
    ids: list[str]
