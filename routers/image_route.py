from fastapi import APIRouter, HTTPException, status

from models.image_models import ImageBase64, ImageCreate, ImageWithUrl
from utils.image_compression import compress_image_to_webp
from utils.utils import separate_data_url_from_base64
from image_recognition.google_vision import check_is_safe_and_contains_cat
from storage.google_cloud_storage import upload_bytes_image, generate_signed_url
from queries.image_queries import insert_image


images_router = APIRouter(prefix="/images", tags=["images"])


@images_router.post("/upload", response_model=ImageWithUrl, status_code=status.HTTP_201_CREATED)
async def post_image(image: ImageBase64):
    base64_data = image.photo_base64
    image_bytes = compress_image_to_webp(separate_data_url_from_base64(base64_data)[1])

    if not check_is_safe_and_contains_cat(image_bytes):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image is not accepted!")
    
    img_file_name_str = upload_bytes_image(image_bytes)
    image_data = ImageCreate(file_name=img_file_name_str)
    new_image = await insert_image(image_data)
    image_url = generate_signed_url(new_image.file_name)
    new_image_with_url = ImageWithUrl(
        image_url=image_url, **new_image.model_dump()
    )

    return new_image_with_url
