# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-11-04 13:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RunPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'run_period',
            },
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('key', models.CharField(choices=[('rates.invites', 'rates.invites'), ('rates.repostsForReposts', 'rates.repostsForReposts'), ('rates.likes', 'rates.likes'), ('period.duration', 'period.duration'), ('period.start', 'period.start'), ('rates.reposts', 'rates.reposts'), ('rates.likesForReposts', 'rates.likesForReposts')], max_length=100, primary_key=True, serialize=False)),
                ('value', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'settings',
            },
        ),
        migrations.CreateModel(
            name='VkGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vk_id', models.IntegerField()),
                ('domain', models.CharField(max_length=150)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'vk_group',
            },
        ),
        migrations.CreateModel(
            name='VkInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkGroup')),
            ],
            options={
                'db_table': 'vk_invite',
            },
        ),
        migrations.CreateModel(
            name='VkPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_id', models.IntegerField()),
                ('text', models.TextField()),
                ('likes_count', models.IntegerField()),
                ('reposts_count', models.IntegerField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkGroup')),
            ],
            options={
                'db_table': 'vk_post',
            },
        ),
        migrations.CreateModel(
            name='VkRepost',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('vk_id', models.IntegerField()),
                ('likes', models.IntegerField(default=0)),
                ('reposts', models.IntegerField(default=0)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkPost')),
            ],
            options={
                'db_table': 'vk_repost',
            },
        ),
        migrations.CreateModel(
            name='VkUser',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50, null=True)),
                ('photo_50', models.URLField(null=True)),
            ],
            options={
                'db_table': 'vk_user',
            },
        ),
        migrations.CreateModel(
            name='VkUserStatisticDaily',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes', models.IntegerField(default=0)),
                ('reposts', models.IntegerField(default=0)),
                ('likes_for_reposts', models.IntegerField(default=0)),
                ('reposts_for_reposts', models.IntegerField(default=0)),
                ('invites', models.IntegerField(default=0)),
                ('date', models.DateField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkGroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkUser')),
            ],
            options={
                'db_table': 'user_statistic_daily',
            },
        ),
        migrations.CreateModel(
            name='VkUserStatisticHourly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes', models.IntegerField(default=0)),
                ('reposts', models.IntegerField(default=0)),
                ('likes_for_reposts', models.IntegerField(default=0)),
                ('reposts_for_reposts', models.IntegerField(default=0)),
                ('invites', models.IntegerField(default=0)),
                ('timestamp', models.DateTimeField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkGroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkUser')),
            ],
            options={
                'db_table': 'user_statistic_hourly',
            },
        ),
        migrations.CreateModel(
            name='VkUserStatisticPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes', models.IntegerField(default=0)),
                ('reposts', models.IntegerField(default=0)),
                ('likes_for_reposts', models.IntegerField(default=0)),
                ('reposts_for_reposts', models.IntegerField(default=0)),
                ('invites', models.IntegerField(default=0)),
                ('total_score', models.IntegerField(default=0)),
                ('rating', models.IntegerField(default=0)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkGroup')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.RunPeriod')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkUser')),
            ],
            options={
                'db_table': 'user_statistic_period',
            },
        ),
        migrations.CreateModel(
            name='VkUserStatisticTotal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes', models.IntegerField(default=0)),
                ('reposts', models.IntegerField(default=0)),
                ('likes_for_reposts', models.IntegerField(default=0)),
                ('reposts_for_reposts', models.IntegerField(default=0)),
                ('invites', models.IntegerField(default=0)),
                ('total_score', models.IntegerField(default=0)),
                ('rating', models.IntegerField(default=0)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkGroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkUser')),
            ],
            options={
                'db_table': 'user_statistic_total',
            },
        ),
        migrations.CreateModel(
            name='VkUserStatisticWeekly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes', models.IntegerField(default=0)),
                ('reposts', models.IntegerField(default=0)),
                ('likes_for_reposts', models.IntegerField(default=0)),
                ('reposts_for_reposts', models.IntegerField(default=0)),
                ('invites', models.IntegerField(default=0)),
                ('week', models.DateField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkGroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkUser')),
            ],
            options={
                'db_table': 'user_statistic_weekly',
            },
        ),
        migrations.AddField(
            model_name='vkrepost',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.VkUser'),
        ),
        migrations.AddField(
            model_name='vkpost',
            name='likes',
            field=models.ManyToManyField(related_name='liked_posts', to='entities.VkUser'),
        ),
        migrations.AddField(
            model_name='vkinvitation',
            name='invited_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='entities.VkUser'),
        ),
        migrations.AddField(
            model_name='vkinvitation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invited_with', to='entities.VkUser'),
        ),
        migrations.AlterUniqueTogether(
            name='vkrepost',
            unique_together=set([('post', 'vk_id', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='vkpost',
            unique_together=set([('group', 'post_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='vkinvitation',
            unique_together=set([('user', 'group')]),
        ),
    ]
