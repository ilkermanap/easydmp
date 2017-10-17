# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-16 08:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plan', '0004_set_editor_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanEditorInvitation',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email_address', models.EmailField(max_length=254)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('sent', models.DateTimeField(blank=True, null=True)),
                ('used', models.DateTimeField(blank=True, null=True)),
                ('invited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plan.Plan')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]