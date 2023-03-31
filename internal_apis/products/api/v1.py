import aiohttp
from fastapi import APIRouter, Query, Path, HTTPException, status
from app.core.config import settings
from ..schemas import QueryResponse
from ..helpers import get_related_product_ids, get_json_response

router = APIRouter()


@router.get("/related_products", response_model=QueryResponse)
async def find_related_products(query: str = Query(...), size: int = Query(10), page: int = Query(0),
                                offset: str = Query(0)):
    return await get_related_product_ids(query, size, page)


@router.get("/products/{product_id}")
async def get_product(product_id: str = Path(...)):
    url = settings.ELASTIC_SEARCH_URL + "/{}/_doc/{}".format(settings.ELASTIC_INDEX, product_id)
    response_body = await get_json_response(url, auth=aiohttp.BasicAuth(settings.ELASTIC_USERNAME,
                                                                        settings.ELASTIC_PASSWORD))
    found = response_body.get("found")
    if found:
        return {
            "id": product_id,
            "category_id": 155,
            **response_body.get("_source")
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

