# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0005_usersitemapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='edx_uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
    ]
