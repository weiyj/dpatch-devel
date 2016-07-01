# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0001_initial'),
        ('engine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patch',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True)),
                ('status', models.IntegerField(default=101, verbose_name='Status', choices=[(101, b'NEW'), (102, b'PATCH'), (103, b'MERGED'), (104, b'RENEW'), (105, b'REPORT'), (201, b'PENDDING'), (301, b'MAILED'), (401, b'FIXED'), (402, b'REMOVED'), (403, b'IGNORED'), (404, b'OBSOLETED'), (405, b'APPLIED'), (406, b'REJECTED'), (407, b'ACCEPTED')])),
                ('file', models.CharField(max_length=256, verbose_name='File Name')),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Date')),
                ('mergered', models.IntegerField(default=0, verbose_name='Mergered')),
                ('mglist', models.CharField(max_length=256, verbose_name='Mergered Patch', blank=True)),
                ('commit', models.CharField(max_length=60, verbose_name='Commit in Git', blank=True)),
                ('module', models.CharField(max_length=60, verbose_name='Module Name', blank=True)),
                ('report', models.TextField(verbose_name='Report', blank=True)),
                ('diff', models.TextField(verbose_name='Diff', blank=True)),
                ('title', models.CharField(max_length=256, verbose_name='Title', blank=True)),
                ('description', models.TextField(max_length=1024, verbose_name='Description', blank=True)),
                ('version', models.IntegerField(default=1, verbose_name='Version')),
                ('emails', models.CharField(max_length=512, verbose_name='Emails', blank=True)),
                ('comment', models.CharField(max_length=256, verbose_name='Comment', blank=True)),
                ('content', models.TextField(verbose_name='Content', blank=True)),
                ('build', models.IntegerField(default=0, verbose_name='Build Status', choices=[(0, b'TBD'), (1, b'PASS'), (2, b'FAIL'), (3, b'WARN'), (4, b'SKIP')])),
                ('buildlog', models.TextField(verbose_name='Build Log', blank=True)),
                ('msgid', models.CharField(max_length=256, verbose_name='Message ID', blank=True)),
                ('tag', models.ForeignKey(verbose_name='Tag', to='repository.RepositoryTag')),
                ('type', models.ForeignKey(verbose_name='Type', to='engine.PatchType')),
            ],
        ),
    ]
