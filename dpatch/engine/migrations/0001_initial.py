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
            name='PatchEngine',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=60, verbose_name='Name')),
                ('status', models.BooleanField(default=False, verbose_name='Enabled')),
                ('flags', models.IntegerField(default=0, verbose_name='Flags')),
                ('setting', models.TextField(verbose_name='Setting', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PatchType',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name='Name', blank=True)),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('comment', models.TextField(verbose_name='Comment', blank=True)),
                ('flags', models.IntegerField(default=0, verbose_name='Flags')),
                ('username', models.CharField(max_length=60, verbose_name='Username', blank=True)),
                ('email', models.CharField(max_length=60, verbose_name='Email', blank=True)),
                ('filename', models.CharField(max_length=256, verbose_name='FileName', blank=True)),
                ('options', models.CharField(max_length=256, verbose_name='Options', blank=True)),
                ('fixed', models.CharField(max_length=256, verbose_name='Fix Regex', blank=True)),
                ('content', models.TextField(verbose_name='Content', blank=True)),
                ('bugfix', models.BooleanField(default=False, verbose_name='Bug Fix')),
                ('reportonly', models.BooleanField(default=False, verbose_name='Report Only')),
                ('includes', models.TextField(verbose_name='Include Paths', blank=True)),
                ('excludes', models.TextField(verbose_name='Exclude Paths', blank=True)),
                ('setting', models.TextField(verbose_name='Setting', blank=True)),
                ('totalfile', models.IntegerField(default=0, verbose_name='TotalFile')),
                ('totaltime', models.IntegerField(default=0, verbose_name='TotalTime')),
                ('status', models.BooleanField(default=False, verbose_name='Enable')),
                ('engine', models.ForeignKey(verbose_name='Engine', to='engine.PatchEngine')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
