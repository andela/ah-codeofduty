# Generated by Django 2.1.2 on 2019-01-03 13:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('surname', models.TextField(blank=True)),
                ('last_name', models.TextField(blank=True)),
                ('avatar', models.URLField(blank=True)),
                ('bio', models.TextField(blank=True)),
                ('bookmarks', models.ManyToManyField(related_name='bookmarks', to='articles.Article')),
                ('favorites', models.ManyToManyField(related_name='favorited_by', to='articles.Article')),
                ('follows', models.ManyToManyField(related_name='followed_by', to='profiles.Profile')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
