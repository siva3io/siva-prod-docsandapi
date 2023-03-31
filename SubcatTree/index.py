from fastapi import APIRouter, HTTPException
import json
import os 


router = APIRouter()


#print(os.listdir())

with open("./SubcatTree/Payload.json", encoding='utf-8', errors='ignore') as json_data:
     data = json.load(json_data, strict=False)


@router.get('/get_subcats')
def get_subcats():
    return data
