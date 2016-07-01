# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='POPServer',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True)),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('server', models.CharField(max_length=256, verbose_name='Server')),
                ('encryption', models.CharField(max_length=256, verbose_name='Encryption')),
                ('port', models.CharField(max_length=20, verbose_name='Port')),
                ('username', models.CharField(max_length=256, verbose_name='Username')),
                ('password', models.CharField(max_length=256, verbose_name='Password')),
                ('email', models.CharField(max_length=256, verbose_name='Email')),
                ('alias', models.CharField(max_length=256, verbose_name='Alias')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SMTPServer',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True)),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('server', models.CharField(max_length=256, verbose_name='Server')),
                ('encryption', models.CharField(max_length=256, verbose_name='Encryption')),
                ('port', models.CharField(max_length=20, verbose_name='Port')),
                ('username', models.CharField(max_length=256, verbose_name='Username')),
                ('password', models.CharField(max_length=256, verbose_name='Password')),
                ('email', models.CharField(max_length=256, verbose_name='Email')),
                ('alias', models.CharField(max_length=256, verbose_name='Alias')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
