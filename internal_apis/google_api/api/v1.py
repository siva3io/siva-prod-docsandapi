import aiohttp

from fastapi import APIRouter, Body
from ..schemas import STTResponse, STTRequest, TranslateRequest, TranslateResponse, \
    ObjectDetectionRequest, ObjectDetectionResponse

from .helpers import extract_text, google_speech_to_text, google_object_detection, google_translate

router = APIRouter()


@router.post("/object_detection", response_model=ObjectDetectionResponse)
async def detect_object_in_image(req_data: ObjectDetectionRequest = Body(...)):
    return await google_object_detection(req_data.file_url, req_data.headers)


@router.post("/text_detection", response_model=dict)
async def detect_text_in_image(req_data: ObjectDetectionRequest = Body(...)):
    async with aiohttp.ClientSession(headers=req_data.headers) as session:
        response = await session.get(req_data.file_url, allow_redirects=True)
        response.raise_for_status()
        content = await response.read()
    detected_text = extract_text(content)
    return {
        "detected_text": detected_text
    }


@router.post("/get_image_details", response_model=dict)
async def detect_text_and_object(req_data: ObjectDetectionRequest = Body(...)):
    async with aiohttp.ClientSession(headers=req_data.headers) as session:
        response = await session.get(req_data.file_url, allow_redirects=True)
        if response.status == 200:
            content = await response.read()
        else:
            return {
                "error": "Error occurred while retrieving image"
            }
    detected_text = extract_text(content)
    if not detected_text:
        detected_text = await google_object_detection(req_data.file_url, req_data.headers).get("detected_objects", [])
    return {
        "result": detected_text
    }


@router.post("/speech_to_text", response_model=STTResponse)
async def get_text_from_audio(req_data: STTRequest = Body(...)):
    result = await google_speech_to_text(req_data.file_url, req_data.headers, req_data.language_code)
    return {
        "detected_text": result
    }


@router.post("/translate", response_model=TranslateResponse)
def translate_text(req_data: TranslateRequest = Body(...)):
    data = {
        'contents': req_data.source_text,
        'target_language_code': req_data.target_language[0],
    }
    return google_translate(data)


