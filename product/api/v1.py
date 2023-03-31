# import json
# import os
#
# from fastapi import APIRouter
# from app.database import Product, UserCart
# from ..helpers import scrape_url
#
# router = APIRouter()
#
#
# @router.post("/add_products")
# async def add_product():
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     data_dir_path = os.path.join(dir_path, '../product_data')
#     # for file_name in os.listdir(data_dir_path):
#     file_path = os.path.join(data_dir_path, 'urls.txt')
#     with open(file_path, 'r') as file:
#         links = file.readlines()
#
#     for scraped_data in scrape_url(links):  # For loop in generator object
#         # Save scraped_data
#         other_data = {}
#         product_overview = scraped_data.get("product_overview", {})
#         if product_overview:
#             for key, value in product_overview.items():
#                 key = key.lower().replace(" ", "_")
#                 other_data[key] = value
#         other_data['store'] = "Amazon"
#         scraped_data["images"] = list(json.loads(scraped_data['images']))
#         print(scraped_data)
#         product_pydantic = Product(**scraped_data, **other_data)
#         product = await Product.objects.create(**product_pydantic.dict())
#         print(product)
