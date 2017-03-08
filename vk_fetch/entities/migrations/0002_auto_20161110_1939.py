# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-11-10 19:39
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vkpost',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='entities.VkUser'),
        ),
        migrations.AddField(
            model_name='vkpost',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 1, 0, 0, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='vkpost',
            name='from_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='settings',
            name='key',
            field=models.CharField(choices=[('rates.likesForReposts', 'rates.likesForReposts'), ('rates.repostsForReposts', 'rates.repostsForReposts'), ('period.start', 'period.start'), ('rates.likes', 'rates.likes'), ('period.duration', 'period.duration'), ('rates.reposts', 'rates.reposts'), ('rates.invites', 'rates.invites')], max_length=100, primary_key=True, serialize=False),
        ),
    ]
