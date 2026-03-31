from django.db.models.signals import post_save
from django.dispatch import receiver

from core.media_optimizer import (
    optimize_image_file,
    optimize_video_file,
    swap_field_file,
)
from core.models import BlogPost, Case, CatalogCar, CatalogCarImage, HeroMedia, Service, TeamMember


def _optimize_image(instance, field_name):
    field_file = getattr(instance, field_name, None)
    if not field_file:
        return
    optimized = optimize_image_file(field_file.path)
    swap_field_file(instance, field_name, optimized)


def _optimize_video(instance, field_name):
    field_file = getattr(instance, field_name, None)
    if not field_file:
        return
    optimized = optimize_video_file(field_file.path)
    swap_field_file(instance, field_name, optimized)


@receiver(post_save, sender=Service)
def optimize_service_media(sender, instance, **kwargs):
    _optimize_image(instance, "image")
    _optimize_video(instance, "video")


@receiver(post_save, sender=HeroMedia)
def optimize_hero_media(sender, instance, **kwargs):
    _optimize_image(instance, "image")
    _optimize_video(instance, "video")


@receiver(post_save, sender=TeamMember)
def optimize_team_member_photo(sender, instance, **kwargs):
    _optimize_image(instance, "photo")


@receiver(post_save, sender=Case)
def optimize_case_media(sender, instance, **kwargs):
    _optimize_image(instance, "image")
    _optimize_video(instance, "video")


@receiver(post_save, sender=CatalogCar)
def optimize_catalog_car_media(sender, instance, **kwargs):
    _optimize_image(instance, "image")
    _optimize_video(instance, "video")


@receiver(post_save, sender=CatalogCarImage)
def optimize_catalog_gallery_photo(sender, instance, **kwargs):
    _optimize_image(instance, "image")


@receiver(post_save, sender=BlogPost)
def optimize_blog_media(sender, instance, **kwargs):
    _optimize_image(instance, "image")
    _optimize_video(instance, "video")
