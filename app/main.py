from fastapi import Request, status, Depends
from fastapi.exceptions import HTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.helpers import get_limiter
from app.helpers import get_application, oauth2_scheme
from app.authentication import router as auth_router
from app.database import database
from ocr.api.v1 import router as ocr_router
from catalog.api.v1 import router as catalog_router
from forecasting.api.v1 import router as forecast_router
from virtual_try_on.api.v1 import router as virtual_try_router
from chatbot.api.v1 import router as chatbot_router
from file_server.api.v1 import router as file_router
from SubcatTree.index import router as subcats_router


tags_metadata = [
    {
        "name": "Catalog",
        "description": "Create Catalog for products. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Cataloging docs",
            "url": "https://eunimart.com/",
        },
    },
    # {
    #     "name": "Chatbot",
    #     # "description": "Get forecasted data by providing present data records"
    # },
    {
        "name": "Image Processing",
        "description": "AI APIs related to image and character recognition",
    },
    {
        "name": "Forecasting",
        "description": "Get forecasted data by providing present data records"
    },
    # {
    #     "name": "Virtual Try On",
    #     # "description": "Get forecasted data by providing present data records"
    # },

]


app = get_application()

app.openapi_tags = tags_metadata
app.state.limiter = get_limiter()
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


async def authentication_required(request: Request, token: str = Depends(oauth2_scheme)):
    # Depends(oauth2_scheme) will add the login form in swagger
    if request.user:
        if not request.user.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login to access the resource."
            )


app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

# app.include_router(catalog_router, prefix="/api/v1/catalog", tags=["Catalog"],
#                    dependencies=[Depends(authentication_required)])
# app.include_router(catalogue_router, prefix="/api/v1/catalog", tags=["Catalog"])
app.include_router(ocr_router, prefix="/api/v1/data_vsion", tags=["Image Processing"],
                   dependencies=[Depends(authentication_required)])
app.include_router(forecast_router, prefix="/api/v1/forecast", tags=["Fosting"],
                   dependencies=[Depends(authentication_required)])
# Virtual Try On not ready yet
# app.include_router(virtual_try_router, prefix="/api/v1/virtual_try_on", tags=["Virtual Try On"],
#                    dependencies=[Depends(authentication_required)])
# app.include_router(chatbot_router, prefix="/api/v1/chatbot", tags=["Chatbot"],
#                    dependencies=[Depends(authentication_required)])
app.include_router(file_router, prefix="/api/v1", tags=["Internal Usage API"])
app.include_router(subcats_router,prefix='/api', tags=["Sub categories Generate API"])


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
