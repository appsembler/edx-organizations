# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-10-27 08:45
from __future__ import unicode_literals

from django.db import migrations, models
import uuid

# APPSEMBLER MIGRATION

class Migration(migrations.Migration):
    """
    Add edx_uuid field to HistoricalMigration.

    Tech-Debt: This is a Tahoe tech-debt that we
               got stuck into and need to clean some day.
    """
    dependencies = [
        ('organizations', '0010_merge_pre_juniper_tahoe'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalorganization',
            name='edx_uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4),
        ),
    ]
