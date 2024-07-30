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


async def select_image_file_name_by_id(image_id: str) -> str:
    image_doc = await image_ref.document(image_id).get()
    image_dict = image_doc.to_dict()
    file_name = image_dict["file_name"]
    return file_name


async def select_all_images() -> list[Image]:
    docs = [doc async for doc in image_ref.stream()]
    images = [Image(id=doc.id, **doc.to_dict()) for doc in docs]
    return images


async def delete_image(image_id: str) -> None:
    image_doc_ref = image_ref.document(image_id)
    await image_doc_ref.delete()
