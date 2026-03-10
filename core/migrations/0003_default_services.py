# Generated data migration: default services for the services page

from django.db import migrations


def create_default_services(apps, schema_editor):
    Service = apps.get_model('core', 'Service')
    defaults = [
        (0, 'Подбор авто на аукционах'),
        (1, 'Выкуп'),
        (2, 'Проверка истории'),
        (3, 'Логистика'),
        (4, 'Таможня'),
        (5, 'Доставка по РФ'),
        (6, 'Оформление'),
        (7, 'Финансирование и лизинг'),
    ]
    for order, title in defaults:
        Service.objects.get_or_create(title=title, defaults={'order': order})


def remove_default_services(apps, schema_editor):
    Service = apps.get_model('core', 'Service')
    titles = [
        'Подбор авто на аукционах', 'Выкуп', 'Проверка истории', 'Логистика',
        'Таможня', 'Доставка по РФ', 'Оформление', 'Финансирование и лизинг',
    ]
    Service.objects.filter(title__in=titles).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_service_model'),
    ]

    operations = [
        migrations.RunPython(create_default_services, remove_default_services),
    ]
