# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-24 10:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cedict', '0005_auto_20160212_1340'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Phrase',
            new_name='Term',
        ),
    ]
