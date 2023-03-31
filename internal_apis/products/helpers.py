import aiohttp
from app.core.config import settings
from google.cloud import language_v1
from internal_apis.google_api.api.helpers import google_translate

CATALOGUE_URL = "https://catalouge.eunimart.com"


async def get_json_response(url, method="GET", body=None, auth=None, json=None, headers={}):
    async with aiohttp.ClientSession(
            headers=headers, auth=auth
    ) as session:
        response = await session.request(method, url, json=json, data=body)
        response.raise_for_status()
        response_body = await response.json()
        return response_body


async def get_related_product_ids(query: str, size: int = 10, page: int = 0):

    url = settings.ELASTIC_SEARCH_URL + f"/_search"
    request_body = {
        "from": page,
        "size": size,
        "query": {
            "query_string": {
                "query": f"{query}~"
            }
        }
    }
    response_body = await get_json_response(
        url=url,
        # auth=aiohttp.BasicAuth(settings.ELASTIC_USERNAME, settings.ELASTIC_PASSWORD),
        json=request_body
    )
    count = response_body.get("hits", {}).get("total", {}).get("value", 0)
    hits = response_body.get("hits", {}).get("hits", [])  # Hits contain the ids of the matching products
    if count != 0:
        ids = [hit.get("_id") for hit in hits]
        return {"query": query, "count": count, "ids": ids}
    return {"query": query, "count": count, "ids": []}


async def get_available_channels(subcategory_id) -> list[int]:
    url = CATALOGUE_URL + "/v2/catalogue/subcategory/available_channels"
    req_payload = {
        "jsonrpc": "2.0",
        "params": {
            "subcategory_id": subcategory_id
        }
    }
    data = await get_json_response(url=url, json=req_payload)
    return data["result"]


async def process_mapped_data(mappings, product_data):
    final_result = []
    url = CATALOGUE_URL + "/catalogue/channels"
    channel_data = await get_json_response(url, json={"jsonrpc": "2.0"})
    channel_data = {channel.get("id"): channel.get("name") for channel in channel_data.get("result")}
    for mapping in mappings:
        channel_id = mapping.get("channel_id")
        final_mapped_data = {
            "channel": channel_data.get(channel_id)
        }
        mapped_attributes = mapping.get("channel_attributes")
        # print("-"*50)
        # print(product_data)
        for data in mapped_attributes:
            value = data["value"]
            field_name = data["name"]
            # print(field_name, "--->", value)
            if value:
                final_mapped_data[field_name] = value
        final_result.append(final_mapped_data)
    return final_result


async def get_mapped_data(product_data):
    product_data["subcategory_id"] = 161
    subcategory_id = product_data["subcategory_id"]
    url = CATALOGUE_URL + '/v2/catalogue/template/attribute_mapping'
    available_channels_ids = await get_available_channels(subcategory_id)

    req_payload = {
        "jsonrpc": "2.0",
        "params": {
            "subcategory_id": subcategory_id,
            "request_channel_id": 22,  # ONDC Channel ID
            "response_channel_id_list": available_channels_ids,
            "request_channel_attributes": product_data
        }
    }
    response_data = await get_json_response(url, method="POST", json=req_payload)
    result = await process_mapped_data(response_data["result"], product_data)
    return result


async def get_translated_text(text_data):
    detected_lang: str = text_data.get("detected_language_code")
    if not detected_lang.startswith("en"):
        data = {
            'contents': [text_data.get("transcript")],
            'target_language_code': "en",
        }
        translated_text = google_translate(data)
        return translated_text.get("translated_text")
    else:
        return text_data.get("transcript")


async def get_entities_in_text(text_data):
    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT
    language = "en"
    document = {"content": text_data, "type_": type_, "language": language}
    encoding_type = language_v1.EncodingType.UTF8
    response = client.analyze_entities(request={'document': document, 'encoding_type': encoding_type})
    return [entity.name for entity in response.entities]

