from django.db import migrations


def create_motorcycle_service(apps, schema_editor):
    Service = apps.get_model('core', 'Service')
    Service.objects.get_or_create(
        title='Продажа мотоциклов',
        defaults={
            'description': 'Мотоциклы из Кореи под заказ и с минимальным пробегом.',
            'media_type': 'image',
            'order': 4,
        },
    )


def remove_motorcycle_service(apps, schema_editor):
    Service = apps.get_model('core', 'Service')
    Service.objects.filter(title='Продажа мотоциклов').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_public_uuid_fields'),
    ]

    operations = [
        migrations.RunPython(create_motorcycle_service, remove_motorcycle_service),
    ]

