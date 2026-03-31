import os

from django.core.exceptions import ValidationError

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}
ALLOWED_VIDEO_EXTENSIONS = {".mp4"}
ALLOWED_VIDEO_MIME_TYPES = {"video/mp4"}

MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_SIZE_BYTES = 50 * 1024 * 1024


def _validate_extension(file_obj, allowed_extensions):
    ext = os.path.splitext((getattr(file_obj, "name", "") or "").lower())[1]
    if ext not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise ValidationError(f"Недопустимое расширение файла. Разрешено: {allowed}.")


def _validate_size(file_obj, max_size_bytes):
    size = getattr(file_obj, "size", 0) or 0
    if size > max_size_bytes:
        max_mb = max_size_bytes // (1024 * 1024)
        raise ValidationError(f"Файл слишком большой. Максимум: {max_mb} MB.")


def _validate_content_type(file_obj, allowed_mime_types):
    content_type = getattr(file_obj, "content_type", None)
    # content_type доступен при upload через формы/админку.
    if content_type and content_type.lower() not in allowed_mime_types:
        allowed = ", ".join(sorted(allowed_mime_types))
        raise ValidationError(f"Недопустимый MIME-тип файла. Разрешено: {allowed}.")


def validate_uploaded_image(file_obj):
    _validate_extension(file_obj, ALLOWED_IMAGE_EXTENSIONS)
    _validate_size(file_obj, MAX_IMAGE_SIZE_BYTES)
    _validate_content_type(file_obj, ALLOWED_IMAGE_MIME_TYPES)


def validate_uploaded_video(file_obj):
    _validate_extension(file_obj, ALLOWED_VIDEO_EXTENSIONS)
    _validate_size(file_obj, MAX_VIDEO_SIZE_BYTES)
    _validate_content_type(file_obj, ALLOWED_VIDEO_MIME_TYPES)
