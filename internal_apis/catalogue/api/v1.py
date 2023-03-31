import re

import aiohttp
from fastapi import APIRouter, Query, Body

from internal_apis.products.helpers import get_related_product_ids, get_mapped_data, \
    get_translated_text, get_entities_in_text
from internal_apis.products.api.v1 import get_product
from internal_apis.google_api.api.helpers import extract_text, google_object_detection
from internal_apis.google_api.api.helpers import google_speech_to_text

router = APIRouter()


@router.get("/text")
async def generate_catalogue_from_text(query: str = Query(...)) -> list[list]:

    #  Get product ids from elastic search
    #  Get product details from elastic (for now)
    #  Pass the data to catalogue api in odoo -> multiple calls for multiple platforms
    #  :return the mapped catalogue data

    data = await get_related_product_ids(query=query, size=5)
    if data.get("count") == 0:
        return []
    product_ids = data.get("ids")
    product_datas = [await get_product(product_id) for product_id in product_ids]
    return [await get_mapped_data(product_data) for product_data in product_datas]


@router.post("/image")
async def generate_catalogue_from_image(image_url: str = Body(...), headers: dict = Body(dict())):

    #  Image --->  Object Detection API ---> name and text (if possible)
    #  Text  --->  generate catalogue from image  --->  Multi platform catalogue
    #  :return catalogue

    async with aiohttp.ClientSession(headers=headers) as session:
        request = await session.get(image_url)
        request.raise_for_status()
        content = await request.read()
    detected_text = extract_text(content)
    if detected_text:
        search_string = ' '.join(detected_text)
        clean_string = re.sub(r'\W+', ' ', search_string)
        print(clean_string)
    # response = {text: await generate_catalogue_from_text(query=text) \
    #             for text in detected_text}
        if search_string:
            response = await generate_catalogue_from_text(query=clean_string)
            if any(response):
                return response
    image_data = await google_object_detection(image_url, headers)
    print("Image URL is", image_url, "Image detected as --->", image_data)
    # TODO: Remove duplicates in detected_objects
    response = {detected_obj[0]: await generate_catalogue_from_text(query=detected_obj[0]) \
                for detected_obj in image_data.get("detected_objects")}
    return response


@router.post("/audio")
async def generate_catalogue_from_audio(file_url: str = Body(...),
                                        language_code: str = Body(...), headers: dict = Body(dict())):
    #  Audio  --->  Speech to text  --->  Get text
    #  Text  --->  Process text (not clear)  -->  Get Product
    #  Text  --->  generate catalogue from image  --->  Multi platform catalogue
    #  :return catalogue

    text_from_audio = await google_speech_to_text(file_url, headers, language_code)
    print(text_from_audio)
    english_sentences = [await get_translated_text(text_data) for text_data in text_from_audio]
    print(text_from_audio, "translated to --->", english_sentences)
    entities = [' '.join(await get_entities_in_text(sentence)) for sentence in english_sentences]
    entities = [entity for entity in entities if entity]
    if not entities:
        return {"error": "Could not find any entities in the audio"}
    print(entities)
    response = [await generate_catalogue_from_text(query=sentence) for sentence in entities]
    return response
