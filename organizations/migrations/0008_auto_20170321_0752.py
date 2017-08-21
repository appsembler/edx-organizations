from django.db import migrations, models
import uuid

# APPSEMBLER MIGRATION

class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0007_auto_20170321_0752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='edx_uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
