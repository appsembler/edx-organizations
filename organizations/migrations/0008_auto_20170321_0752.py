from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0007_auto_20170321_0752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
