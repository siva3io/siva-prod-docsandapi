import base64
import re

import aiohttp
from fastapi import APIRouter, Request, File, Body, Depends, HTTPException, status

from ocr.schemas import OCRResponse, ImageFile, ObjectDetectionResponse
from app.helpers import get_limiter
from ocr.api.helpers import get_easyocr_reader, get_image
from ..object_detection.main import run

router = APIRouter()
limiter = get_limiter()

PAN_REGEX = r"[A-Z]{3}[ABCFGHLJPTF]{1}[A-Z]{1}[0-9]{4}[A-Z]{1}"
AADHAR_REGEX = r"\d{12}|\d{4} \d{4} \d{4}"


def read_text_from_image(image):
    reader = get_easyocr_reader()
    result = reader.readtext(image, detail=0, paragraph=False)
    return result


async def detect_object_in_image(image: str):
    result = run(source=image)
    result = result.split(" ")[0]
    return result


@router.post("/recognize_text", name="Optical Character Recognition",
             description="Recognize and extract text data from an image", response_model=OCRResponse
             )
@limiter.limit("5/minute")
async def post_ocr_api(request: Request, image_file: bytes = File(None),
                       image: str = Body(None, description="Image as base64 string or live image url"),
                       ):
    if image_file is None:
        image_file = image
    cv2_image = await get_image(image_file)
    result = read_text_from_image(cv2_image)
    return {"detected_text": result}


@router.post("/object_detection", response_model=ObjectDetectionResponse)
async def identify_object(request: Request,
                          image: ImageFile = Body(None,
                                                  description="Image as base64 string or URL available for public")
                          ):
    image = image.image
    if image.startswith("http"):

        async with aiohttp.ClientSession() as session:
            response = await session.get(image)
            if response.status >= 300:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Error in retrieving image from given url!")
            encoded_image = base64.b64encode(await response.read()).decode('utf-8')
    else:
        encoded_image = image
    result = await detect_object_in_image(encoded_image)  # Find the object
    response = {
        "detected_object": result
    }
    return response


@router.post("/get_aadhar_number", name="Extract Aadhar number from Aadhar Image",
             description="Recognize and extract aadhar data from image", response_model=OCRResponse
             )
@limiter.limit("5/minute")
async def aadhar_number_api(request: Request, image_file: bytes = File(None),
                            image: str = Body(None, description="Image as base64 string or live image url"),
                            ):
    if image_file is None:
        image_file = image
    cv2_image = await get_image(image_file)
    result = read_text_from_image(cv2_image)
    aadhar_regex = re.compile(AADHAR_REGEX)
    aadhar_text = ' '.join([str(x) for x in result])
    print(aadhar_text)
    aadhar_numbers = aadhar_regex.findall(aadhar_text)
    if len(aadhar_numbers) > 0:
        aadhar_number = aadhar_numbers[0]
    else:
        aadhar_number = ""
    return {"detected_text": [aadhar_number]}


@router.post("/get_pan_number", name="Extract PAN number from Image",
             description="Recognize and extract PAN data from image", response_model=OCRResponse
             )
@limiter.limit("5/minute")
async def pan_number_api(request: Request, image_file: bytes = File(None),
                         image: str = Body(None, description="Image as base64 string or live image url"),
                         ):
    if image_file is None:
        image_file = image
    cv2_image = await get_image(image_file)
    result = read_text_from_image(cv2_image)
    pan_regex = re.compile(PAN_REGEX)
    pan_text = ' '.join([str(x) for x in result])
    pan_number = ''.join(pan_regex.findall(pan_text))
    if pan_number == "":
        pan_regex = re.compile(r"[A-Z0-9]{10}")
        possible_pan_numbers = pan_regex.findall(pan_text)
        print(possible_pan_numbers)
        for value in possible_pan_numbers:
            if value.isalnum() and not value.isalpha():
                pan_number = value
    return {"detected_text": [pan_number]}
