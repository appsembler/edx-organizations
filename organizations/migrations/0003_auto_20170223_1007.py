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
            name='site',
            field=models.OneToOneField(related_name='organization', null=True, blank=True, to='sites.Site'),
        ),
        migrations.AlterField(
            model_name='userorganizationmapping',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
