from typing import Optional, Union

from pydantic import BaseModel, Field


class BotSessionRequest(BaseModel):
    user_id: int
    token: Optional[str]


class BotSessionResponse(BaseModel):
    conversation_id: str
    message: str


class MessageRequest(BaseModel):
    conversation_id: str
    message_content: str


class BotResponse(BaseModel):
    text: str
    sequence: int
    sequence_next: int


class BotButton(BaseModel):
    button_id: str
    title: str = Field(alias="text/title")
    sequence: int
    sequence_next: int


class MessageResponse(BaseModel):
    conversation_id: str = Field(alias="conversation_id/uuid")
    responses: list[BotResponse]
    buttons: list[BotButton]


class OptionRequest(BaseModel):
    conversation_id: str
    button_id: int
    payload: Optional[dict]


class OptionResponse(MessageResponse):
    name: str
    button_id: int


class OdooJsonRequest(BaseModel):
    jsonrpc: str = "2.0"
    params: dict = {}


class CategoryResponse(BaseModel):
    category_id: int
    category_name: str


class SubCategoryResponse(BaseModel):
    subcategory_id: int
    subcategory_name: str


class Channel(BaseModel):
    id: int
    name: str
    sequence: int
    channel_type: str


class ChannelFieldRequest(BaseModel):
    subcategory_id: int
    channel_id_list: list[int]


class ChannelAttributes(BaseModel):
    id: int
    name: str
    type: str
    allowed_values: dict
    attribute_description: Union[bool, str]
    attribute_validation_regex: bool
    is_mandatory: bool
    is_predictable: bool
    display_name: str
    source: str
    prediction_route_endpoint: str
    prediction_params: list
    is_prefilled: Optional[bool]
    prefilled_value: Optional[str]


class ChannelFieldResponse(BaseModel):
    channel_id: int
    channel_attribute_version: int
    channel_attributes: list[ChannelAttributes]


class ChannelAttribute(BaseModel):
    sku_id: str = Field(alias="sku_id/child_sku")  # The response is mixed for name and id
    subcategory_name: int
    relation: str
    osion: str
    pattern: str
    product_title: str
    product_description: str
    product_image: str


class AttributeMapRequest(BaseModel):
    subcategory_id: int
    request_channel_id: int
    response_channel_id_list: list[int]
    request_channel_attributes: ChannelAttribute


class AttributeValuePredictRequest(BaseModel):
    channel_id: int
    attribute_id: int
    attribute_name: str
    url: str
    product_title: str


class AttributePredictResponse(BaseModel):
    attribute_name: str
    attribute_value: str
