# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

# APPSEMBLER MIGRATION

class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0004_auto_20170212_1223'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSiteMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_amc_admin', models.BooleanField(default=False)),
                ('site', models.ForeignKey(to='sites.Site')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
