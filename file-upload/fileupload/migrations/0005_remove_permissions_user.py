# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-08 09:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fileupload', '0004_permissions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permissions',
            name='user',
        ),
    ]
