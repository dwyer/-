# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-29 09:31
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('texts', '0004_phrase_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='text',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 2, 29, 9, 31, 56, 460510)),
            preserve_default=False,
        ),
    ]
