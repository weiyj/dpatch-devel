# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-28 07:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0002_patchtype_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='patchengine',
            name='total',
            field=models.IntegerField(default=0, verbose_name='Total Types'),
        ),
    ]