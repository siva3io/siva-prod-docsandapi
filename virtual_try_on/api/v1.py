from fastapi import APIRouter, Request
from app.helpers import get_limiter

router = APIRouter()
limiter = get_limiter()


@router.post("/", name="Virtual Try On")
@limiter.limit("5/minute")
def get_virtual_try_on(request: Request):
    return "virtual_try_on feature yet to be added!"
