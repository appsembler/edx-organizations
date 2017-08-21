# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

# APPSEMBLER MIGRATION

class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_organization_sites'),
    ]

    operations = [
        migrations.AddField(
            model_name='userorganizationmapping',
            name='is_amc_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userorganizationmapping',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
