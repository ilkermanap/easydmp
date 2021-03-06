# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-05 07:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plan', '0020_make_plan_clonable'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cloned_when', models.DateTimeField(blank=True, null=True)),
                ('may_edit', models.NullBooleanField()),
                ('cloned_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clones', to='plan.PlanAccess')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accesses', to='plan.Plan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plan_accesses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='planaccess',
            unique_together=set([('user', 'plan')]),
        ),
    ]
