from fastapi import APIRouter

from routers import user_route, image_route


api_router = APIRouter()
api_router.include_router(user_route.user_router)
api_router.include_router(image_route.images_router)
