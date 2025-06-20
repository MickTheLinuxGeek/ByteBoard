# Generated by Django 5.2.1 on 2025-06-14 00:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
        ('forum', '0005_alter_profile_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='topics', to='categories.category'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, help_text='Upload your avatar image', null=True, upload_to='avatars/'),
        ),
    ]
