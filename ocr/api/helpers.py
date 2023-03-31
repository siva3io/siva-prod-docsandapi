import base64

import aiohttp
import easyocr
import cv2
import numpy as np
from fastapi import HTTPException
from starlette import status


# import subprocess
# print(subprocess.run(["pip", "freeze"]))


def get_easyocr_reader():
    reader = easyocr.Reader(['en'])
    return reader


async def get_image(image):
    if type(image) is bytes:
        encoded_image = base64.b64encode(image)
    else:
        encoded_image = image
        if image and image.startswith('http'):
            async with aiohttp.ClientSession() as session:
                response = await session.get(image, allow_redirects=True)
                if response.status >= 300:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        detail="Image cannot be retrieved from the provided URL! Kindly provide a valid URL.")
                image_bytes = await response.read()
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        if image and image.startswith("b"):
            encoded_image = image[1:]
    np_array = np.fromstring(base64.b64decode(encoded_image), np.uint8)
    img = cv2.imdecode(np_array, 0)
    return img
