# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('organizations', '0002_auto_20160511_0811'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='sites',
            field=models.ManyToManyField(related_name='organizations', to='sites.Site'),
        ),
    ]
