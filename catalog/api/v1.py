import aiohttp
from fastapi import APIRouter, Request, Query
from app.helpers import get_limiter
from chatbot.schemas import OdooJsonRequest, CategoryResponse, Channel, ChannelFieldResponse, ChannelFieldRequest, \
    AttributeMapRequest, AttributeValuePredictRequest, AttributePredictResponse, SubCategoryResponse

router = APIRouter()
limiter = get_limiter()

BASE_URL = "https://catalouge.eunimart.com"


@router.get("/categories", response_model=list[CategoryResponse])
@limiter.limit("5/minute")
async def get_categories(request: Request):
    data = OdooJsonRequest().dict()
    async with aiohttp.ClientSession() as session:
        url = BASE_URL + "/catalogue/categories"
        async with session.post(url, json=data) as response:
            response = await response.json()
            return response.get("result")


@router.get("/subcategories", response_model=list[SubCategoryResponse])
@limiter.limit("5/minute")
async def get_subcategories(request: Request, category_id: int = Query()):
    data = OdooJsonRequest(params={"category_id": category_id}).dict()
    async with aiohttp.ClientSession() as session:
        url = BASE_URL + "/catalogue/subcategories"
        async with session.post(url, json=data) as response:
            response = await response.json()
            return response.get("result")


@router.get("/channels", response_model=list[Channel])
@limiter.limit("5/minute")
async def get_all_channels(request: Request):
    data = OdooJsonRequest().dict()
    async with aiohttp.ClientSession() as session:
        url = BASE_URL + "/catalogue/channels"
        async with session.post(url, json=data) as response:
            response = await response.json()
            return response.get("result")


@router.get("/available_channels", response_model=list[int])
@limiter.limit("5/minute")
async def list_available_channels(request: Request, subcategory_id: int = Query()):
    data = OdooJsonRequest(params={"subcategory_id": subcategory_id}).dict()
    async with aiohttp.ClientSession() as session:
        url = BASE_URL + "/v2/catalogue/subcategory/available_channels"
        async with session.post(url, json=data) as response:
            response = await response.json()
            return response.get("result")


@router.post("/subcategory/channels/fields", response_model=list[ChannelFieldResponse])
@limiter.limit("5/minute")
async def list_channel_fields(request: Request, params_data: ChannelFieldRequest):
    data = OdooJsonRequest(params=params_data.dict()).dict()
    async with aiohttp.ClientSession() as session:
        url = BASE_URL + "/catalogue/subcategory/channels/fields"
        async with session.post(url, json=data) as response:
            response = await response.json()
            return response.get("result")


@router.post("/attribute_mapping", response_model=list[ChannelFieldResponse])
@limiter.limit("5/minute")
async def catalogue_attribute_mapping(request: Request, params_data: AttributeMapRequest):
    data = OdooJsonRequest(params=params_data.dict()).dict()
    async with aiohttp.ClientSession() as session:
        url = BASE_URL + "/catalogue/template/attribute_mapping"
        async with session.post(url, json=data) as response:
            response = await response.json()
            return response.get("result")


@router.post("/predict_attribute", response_model=AttributePredictResponse)
@limiter.limit("5/minute")
async def predict_attribute(request: Request, params_data: AttributeValuePredictRequest):
    data = OdooJsonRequest(params=params_data.dict()).dict()
    async with aiohttp.ClientSession() as session:
        url = BASE_URL + "/catalogue/predict"
        async with session.post(url, json=data) as response:
            response = await response.json()
            return response.get("result")
