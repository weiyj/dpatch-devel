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
            name='FileChecksum',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True)),
                ('file', models.CharField(max_length=256, verbose_name='File Name')),
                ('checksum', models.CharField(max_length=60, verbose_name='Checksum')),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Date')),
            ],
        ),
        migrations.CreateModel(
            name='FileModule',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name='Module Name')),
                ('file', models.CharField(max_length=256, verbose_name='File Name')),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True)),
                ('type', models.IntegerField(default=0, verbose_name='Type', choices=[(0, b'kernel')])),
                ('name', models.CharField(max_length=60, verbose_name='Name')),
                ('url', models.CharField(max_length=256, verbose_name='URL')),
                ('protocol', models.IntegerField(default=0, verbose_name='Protocol', choices=[(0, b'git')])),
                ('username', models.CharField(max_length=60, verbose_name='Username')),
                ('email', models.CharField(max_length=256, verbose_name='Email')),
                ('developing', models.BooleanField(default=False, verbose_name='Developing')),
                ('devel', models.CharField(default=None, max_length=60, null=True, verbose_name='Development Tree')),
                ('build', models.BooleanField(default=True, verbose_name='Enable Build')),
                ('commit', models.CharField(max_length=256, verbose_name='Last Commit', blank=True)),
                ('stable', models.CharField(max_length=256, verbose_name='Stable Commit', blank=True)),
                ('update', models.DateTimeField(auto_now=True, verbose_name='Last Update')),
                ('includes', models.TextField(verbose_name='Include Paths', blank=True)),
                ('excludes', models.TextField(verbose_name='Exclude Paths', blank=True)),
                ('status', models.BooleanField(default=False, verbose_name='Enabled')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RepositoryHistory',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True)),
                ('changes', models.IntegerField(default=0, verbose_name='Change')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Date')),
                ('repo', models.ForeignKey(verbose_name='Repository', to='repository.Repository')),
            ],
        ),
        migrations.CreateModel(
            name='RepositoryTag',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=60, verbose_name='Name')),
                ('total', models.IntegerField(default=0, verbose_name='Total Patchs')),
                ('changelist', models.TextField(verbose_name='Changed Files', blank=True)),
                ('running', models.BooleanField(default=False, verbose_name='Running')),
                ('repo', models.ForeignKey(verbose_name='Repository', to='repository.Repository')),
            ],
        ),
        migrations.AddField(
            model_name='filemodule',
            name='repo',
            field=models.ForeignKey(verbose_name='Repository', to='repository.Repository'),
        ),
        migrations.AddField(
            model_name='filechecksum',
            name='repo',
            field=models.ForeignKey(verbose_name='Repository', to='repository.Repository'),
        ),
    ]
