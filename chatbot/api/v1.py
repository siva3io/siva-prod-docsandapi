import json

import aiohttp
from fastapi import APIRouter, Request

from app.helpers import get_limiter
from ..schemas import BotSessionRequest, BotSessionResponse, MessageRequest, MessageResponse, OptionResponse, \
    OptionRequest

router = APIRouter()
limiter = get_limiter()
BASE_URL = "https://odoo-test.eunimart.com"


# @router.get("/")
# @limiter.limit("5/minute")
# def get_chatbot():
#     return "chatbot app created!"


@router.post("/session", response_model=BotSessionResponse, description="Pass the token and user id")
@limiter.limit("5/minute")
async def initiate_session(request: Request, request_data: BotSessionRequest):

    async with aiohttp.ClientSession() as session:
        url = BASE_URL + "/rasachatbot/create_session?db=odoo&username=admin&password=admin"
        response = await session.post(url=url, json=request_data.dict())
    response_json = await response.json()
    result = response_json.get("result")
    return result


@router.post("/message", description="Use the conversation id from session!",
             response_model=MessageResponse)
@limiter.limit("5/minute")
async def message_response(request: Request, request_data: MessageRequest):

    async with aiohttp.ClientSession() as session:
        url = BASE_URL + "/rasachatbot/post_message"
        response = await session.post(url=url, json=request_data.dict())
    response_json = await response.json()
    result = response_json.get("result")
    return result


@router.post("/option", description="Use the conversation id from session!",
             response_model=OptionResponse)
@limiter.limit("5/minute")
async def button_response(request: Request, request_data: OptionRequest):

    async with aiohttp.ClientSession() as session:
        url = BASE_URL + "/rasachatbot/button_response"
        response = await session.post(url=url, json=request_data.dict())
    response_json = await response.json()
    result = response_json.get("result")
    return result
