# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-22 09:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dmpt', '0003_auto_20170921_1220'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('section', 'position')},
        ),
        migrations.AlterField(
            model_name='question',
            name='position',
            field=models.PositiveIntegerField(default=1, help_text='Position in section. Must be unique.'),
        ),
        migrations.AlterField(
            model_name='question',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='dmpt.Section'),
        ),
        migrations.AlterField(
            model_name='section',
            name='position',
            field=models.PositiveIntegerField(default=1, help_text='A specific position may only occur once per template'),
        ),
        migrations.AlterField(
            model_name='section',
            name='title',
            field=models.CharField(blank=True, help_text='May be empty for **one** section per template', max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name='question',
            unique_together=set([('section', 'position')]),
        ),
        migrations.AlterUniqueTogether(
            name='section',
            unique_together=set([('template', 'title'), ('template', 'position')]),
        ),
    ]
