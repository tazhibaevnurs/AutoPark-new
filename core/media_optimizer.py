import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


MAX_IMAGE_WIDTH = 1600
MAX_IMAGE_HEIGHT = 1600
IMAGE_QUALITY = 82

MAX_VIDEO_WIDTH = 1280
VIDEO_CRF = "28"
VIDEO_PRESET = "veryfast"
AUDIO_BITRATE = "96k"


def _is_optimized_image(path):
    return path.suffix.lower() == ".webp" and path.stem.endswith("_optimized")


def _is_optimized_video(path):
    return path.suffix.lower() == ".mp4" and path.stem.endswith("_optimized")


def optimize_image_file(file_path):
    """
    Конвертирует изображение в WebP и ограничивает размер.
    Возвращает path оптимизированного файла или исходный path.
    """
    src = Path(file_path)
    if not src.exists() or _is_optimized_image(src):
        return src

    optimized = src.with_name(f"{src.stem}_optimized.webp")
    with Image.open(src) as img:
        img = img.convert("RGB")
        img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT))
        img.save(optimized, format="WEBP", quality=IMAGE_QUALITY, optimize=True)
    return optimized


def optimize_video_file(file_path):
    """
    Сжимает видео через ffmpeg в mp4 с ограничением ширины.
    Возвращает path оптимизированного файла или исходный path.
    """
    src = Path(file_path)
    if not src.exists() or _is_optimized_video(src):
        return src
    if shutil.which("ffmpeg") is None:
        return src

    optimized = src.with_name(f"{src.stem}_optimized.mp4")
    if optimized.exists():
        return optimized

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_output = Path(temp_file.name)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(src),
        "-vf",
        f"scale='min({MAX_VIDEO_WIDTH},iw)':-2",
        "-c:v",
        "libx264",
        "-preset",
        VIDEO_PRESET,
        "-crf",
        VIDEO_CRF,
        "-movflags",
        "+faststart",
        "-c:a",
        "aac",
        "-b:a",
        AUDIO_BITRATE,
        str(temp_output),
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        temp_output.replace(optimized)
    except (subprocess.CalledProcessError, OSError):
        if temp_output.exists():
            temp_output.unlink(missing_ok=True)
        return src
    return optimized


def swap_field_file(instance, field_name, optimized_path):
    """
    Подменяет файл модели на оптимизированный и удаляет старый файл.
    """
    field_file = getattr(instance, field_name)
    if not field_file or not optimized_path:
        return False

    current_path = Path(field_file.path)
    optimized_path = Path(optimized_path)
    if not optimized_path.exists() or current_path == optimized_path:
        return False

    base_media = Path(instance._meta.get_field(field_name).storage.location)
    relative_name = optimized_path.relative_to(base_media).as_posix()
    setattr(instance, field_name, relative_name)
    instance.save(update_fields=[field_name])

    if current_path.exists():
        current_path.unlink(missing_ok=True)
    return True
