from pydantic import BaseModel, Field
from typing import List, Dict


class Schema(BaseModel):
    field_label: str = Field(description="Name/Label of the field")
    field_type: str
    field_sequence: int
    is_y: bool
    is_collinear: bool
    collinear_fields: List


class ForecastData(BaseModel):
    data_type: str
    schema_: List[Schema] = Field(alias="schema")
    data: Dict
    alpha: float
    lead: int
    query_id: str

    class Config:
        schema_extra = {
            "example": {
                    "data_type": "time_series",
                    "schema": [
                        {
                            "field_label": "Month",
                            "field_type": "date",
                            "field_sequence": 0,
                            "is_y": False,
                            "is_collinear": False,
                            "collinear_fields": []
                        },
                        {
                            "field_label": "Sales",
                            "field_type": "int",
                            "field_sequence": 1,
                            "is_y": True,
                            "is_collinear": False,
                            "collinear_fields": []
                        }
                    ],
                    "data": {
                        "Month": [
                            "1964-01",
                            "1964-02",
                            "1964-03",
                        ],
                        "Sales": [
                            2815.0,
                            2672.0,
                            2755.0,
                        ]
                    },
                    "alpha": "0.9",
                    "lead": "62",
                    "query_id": "nc3948g57guwy3458768yhfn"
                }
            }


class ForecastResponse(BaseModel):
    datetime: List
    y_label_low: List
    y_label_high: List
    y_label_mean: List
    # query_id: str
