# Generated manually — аудит: уникальные роли вместо шаблонного текста

from django.db import migrations


DUP_SNIPPET = 'Ведущий эксперт по подбору автомобилей'


def forwards(apps, schema_editor):
    TeamMember = apps.get_model('core', 'TeamMember')
    updates = {
        'Александр Якубов': (
            'Подбор и сопровождение сделок с Кореей и Китаем: аукционы, проверка лотов, связь с поставщиками.'
        ),
        'Никита Настенко': (
            'Логистика и сроки: маршруты доставки, контроль загрузки и таможенного оформления.'
        ),
        'Евгений Певтиев': (
            'Таможня и документы: расчёт платежей, ПТС, постановка на учёт.'
        ),
        'Роман Юковичь': (
            'Работа с аукционами США и оценка состояния авто по инспекциям и отчётам.'
        ),
    }
    for name, role in updates.items():
        TeamMember.objects.filter(name=name, role__contains=DUP_SNIPPET).update(role=role)


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_default_motorcycle_service'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
