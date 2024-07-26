from pydantic import BaseModel


class ImageBase(BaseModel):
    file_name: str 


class ImageUrl:
    image_url: str


class ImageBase64(BaseModel):
    photo_base64: str


class ImageCreate(ImageBase):
    pass


class Image(ImageBase):
    id: str


class ImageWithUrl(Image, ImageUrl):
    pass 
