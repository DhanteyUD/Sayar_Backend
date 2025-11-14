import cloudinary
import cloudinary.uploader
import cloudinary.api
from ..core.config import settings


class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

    # noinspection PyMethodMayBeStatic
    def upload_image(self, image_file, folder: str = "sayar/products") -> dict:
        """Upload image to Cloudinary"""
        try:
            result = cloudinary.uploader.upload(
                image_file,
                folder=folder,
                transformation=[
                    {"width": 800, "height": 600, "crop": "limit"},
                    {"quality": "auto"},
                    {"format": "webp"}
                ]
            )
            return {
                "public_id": result["public_id"],
                "url": result["secure_url"],
                "format": result["format"],
                "width": result["width"],
                "height": result["height"]
            }
        except Exception as e:
            raise Exception(f"Image upload failed: {str(e)}")

    # noinspection PyMethodMayBeStatic
    def delete_image(self, public_id: str) -> dict:
        """Delete image from Cloudinary"""
        try:
            return cloudinary.uploader.destroy(public_id)
        except Exception as e:
            raise Exception(f"Image deletion failed: {str(e)}")

    def update_image(self, public_id: str, image_file) -> dict:
        """Update existing image"""
        try:
            self.delete_image(public_id)
            return self.upload_image(image_file)
        except Exception as e:
            raise Exception(f"Image update failed: {str(e)}")


cloudinary_service = CloudinaryService()