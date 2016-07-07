# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-07 16:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0005_vkuserstatistictotal_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='VkRepost',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('vk_id', models.IntegerField()),
                ('likes', models.IntegerField(default=0)),
                ('reposts', models.IntegerField(default=0)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkPost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkUser')),
            ],
            options={
                'db_table': 'vk_repost',
            },
        ),
        migrations.AddField(
            model_name='vkuserstatisticdaily',
            name='likes_for_reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vkuserstatisticdaily',
            name='reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vkuserstatisticdaily',
            name='reposts_for_reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vkuserstatistichourly',
            name='likes_for_reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vkuserstatistichourly',
            name='reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vkuserstatistichourly',
            name='reposts_for_reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vkuserstatistictotal',
            name='likes_for_reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vkuserstatistictotal',
            name='reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vkuserstatistictotal',
            name='reposts_for_reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vkuserstatisticweekly',
            name='likes_for_reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vkuserstatisticweekly',
            name='reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vkuserstatisticweekly',
            name='reposts_for_reposts',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='vkrepost',
            unique_together=set([('post', 'vk_id', 'user')]),
        ),
    ]
