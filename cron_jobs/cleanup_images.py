from queries.image_queries import select_all_images, delete_image
from queries.cat_queries import check_image_relates_to_cotw, check_image_relates_to_crc, check_image_relates_to_nrc
from storage.google_cloud_storage import delete_blob_by_file_name


async def cleanup_unused_images():
    existing_images = await select_all_images()

    for image in existing_images:
        if not any([
            await check_image_relates_to_nrc(image.id),
            await check_image_relates_to_crc(image.id),
            await check_image_relates_to_cotw(image.id),
        ]):
            await delete_image(image.id)
            delete_blob_by_file_name(image.file_name)
