# Generated by Django 4.1.6 on 2023-04-05 09:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import froala_editor.fields
import hadesapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('hadesapp', '0005_alter_appeal_checked_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('snippet', models.CharField(max_length=255)),
                ('content', froala_editor.fields.FroalaField()),
                ('cover_picture', models.ImageField(blank=True, null=True, upload_to=hadesapp.models.article_cover_path)),
                ('game', models.ManyToManyField(blank=True, related_name='article_about_game', to='hadesapp.game')),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]