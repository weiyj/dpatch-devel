# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemsetting',
            name='update',
            field=models.DateTimeField(auto_now=True, verbose_name='Last Update'),
        ),
    ]
