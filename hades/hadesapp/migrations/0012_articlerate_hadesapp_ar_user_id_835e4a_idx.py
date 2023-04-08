# Generated by Django 4.1.6 on 2023-04-08 09:33

from django.db import migrations
import psqlextra.indexes.unique_index


class Migration(migrations.Migration):

    dependencies = [
        ('hadesapp', '0011_alter_article_games'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='articlerate',
            index=psqlextra.indexes.unique_index.UniqueIndex(fields=['user', 'article'], name='hadesapp_ar_user_id_835e4a_idx'),
        ),
    ]