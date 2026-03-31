import uuid

from django.db import migrations, models


def fill_public_ids(apps, schema_editor):
    for model_name in ("Service", "Case", "CatalogCar", "BlogPost"):
        Model = apps.get_model("core", model_name)
        for obj in Model.objects.filter(public_id__isnull=True):
            obj.public_id = uuid.uuid4()
            obj.save(update_fields=["public_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_blog_post"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="public_id",
            field=models.UUIDField(db_index=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="case",
            name="public_id",
            field=models.UUIDField(db_index=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="catalogcar",
            name="public_id",
            field=models.UUIDField(db_index=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="public_id",
            field=models.UUIDField(db_index=True, editable=False, null=True),
        ),
        migrations.RunPython(fill_public_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="service",
            name="public_id",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="case",
            name="public_id",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="catalogcar",
            name="public_id",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="public_id",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
