# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-27 14:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patchtype',
            name='source',
            field=models.IntegerField(choices=[(0, b'define'), (1, b'kernel')], default=0, verbose_name='Source'),
        ),
    ]
