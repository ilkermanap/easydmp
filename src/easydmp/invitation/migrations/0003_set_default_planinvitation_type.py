# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-08 07:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0002_rename_planeditorinvitation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planinvitation',
            name='type',
            field=models.CharField(choices=[('edit', 'Edit'), ('view', 'View')], default='view', max_length=4),
        ),
    ]
