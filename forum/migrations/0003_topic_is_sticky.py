# Generated by Django 5.2.1 on 2025-05-20 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_post_updated_at_alter_post_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='is_sticky',
            field=models.BooleanField(default=False),
        ),
    ]
