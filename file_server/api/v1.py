import base64
import aiofiles
from fastapi import APIRouter, Body


router = APIRouter()


@router.post("/base64_to_image")
async def store_base64_image(base64_image: str = Body(...), image_name: str = Body(...),image_type: str = Body("jpg")):
    image_content = base64.b64decode(base64_image)
    async with aiofiles.open(f"/datadrive/static/images/{image_name}.{image_type}", 'wb') as file:
        await file.write(image_content)
        return {
            "status": "success"
        }
