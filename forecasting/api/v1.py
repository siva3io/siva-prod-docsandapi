import aiohttp

from fastapi import APIRouter, Request
from app.helpers import get_limiter
from ..schemas import ForecastData, ForecastResponse

router = APIRouter()
limiter = get_limiter()


# @router.get("/")
# @limiter.limit("5/minute")
# def get_forecasting(request: Request):
#     return "This api used for dynamic forecasting!"


@router.post("/", response_model=ForecastResponse)
@limiter.limit("20/minute")
async def forecast_data(request: Request, forecast_params: ForecastData):
    async with aiohttp.ClientSession() as session:
        data = {"data": forecast_params.dict()}
        data["data"]["schema"] = data["data"]["schema_"]
        url = "http://40.80.88.97/forecasting/forecasting"
        async with session.post(url, json=data) as response:
            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])

            response = await response.json()
            result = response.get("result", {}).get("data")
            return result
