from db import db
from models.image_models import ImageCreate, Image


image_ref = db.collection("Images")


async def insert_image(image_data: ImageCreate) -> Image:
    new_image_ref = image_ref.document()
    image_data_dict = image_data.model_dump()
    await new_image_ref.set(image_data_dict)
    image_data_dict["id"] = new_image_ref.id
    image = Image(**image_data_dict)
    return image
    