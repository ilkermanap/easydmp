# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-13 10:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dmpt', '0007_add_externalchoicequestion'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalMultipleChoiceOneTextQuestion',
            fields=[
            ],
            options={
                'indexes': [],
                'proxy': True,
            },
            bases=('dmpt.question',),
        ),
        migrations.AlterField(
            model_name='question',
            name='input_type',
            field=models.CharField(choices=[('bool', 'bool'), ('choice', 'choice'), ('daterange', 'daterange'), ('multichoiceonetext', 'multichoiceonetext'), ('reason', 'reason'), ('positiveinteger', 'positiveinteger'), ('externalchoice', 'externalchoice'), ('externalmultichoiceonetext', 'externalmultichoiceonetext')], max_length=32),
        ),
    ]
