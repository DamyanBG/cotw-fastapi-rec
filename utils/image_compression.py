from PIL import Image
from base64 import b64decode
from io import BytesIO
from binascii import Error


def compress_image_to_webp(base64_image: str) -> bytes:
    max_size = 200 * 1024
    file_type = "webp"
    quality = 85
    try:
        image_data = b64decode(base64_image)

        if len(image_data) > max_size:
            img = Image.open(BytesIO(image_data))
            buffer = BytesIO()

            img.save(buffer, format=file_type, lossless=False, quality=quality)
            buffer.seek(0)
            image_data = buffer.read()

        return image_data

    except (Error, Image.UnidentifiedImageError) as e:
        raise ValueError("Invalid image data or format") from e
