# Generated by Django 2.1.2 on 2018-11-16 10:45

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=255)),
                ('body', models.TextField()),
                ('images', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, default=None, null=True, size=None)),
                ('description', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=40, unique=True)),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), blank=True, default=None, null=True, size=None)),
                ('time_to_read', models.IntegerField()),
                ('time_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('time_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('average_rating', models.IntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articles', to=settings.AUTH_USER_MODEL)),
                ('dislikes', models.ManyToManyField(blank=True, related_name='_article_dislikes_+', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(blank=True, related_name='_article_likes_+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('time_created', 'time_updated'),
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='articles.Article')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(blank=True, related_name='comment_likes', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='thread', to='articles.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='CommentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('parent_comment', models.ForeignKey(db_column='parent_comment', on_delete=django.db.models.deletion.CASCADE, to='articles.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='Highlight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index_start', models.IntegerField(default=0)),
                ('index_stop', models.IntegerField()),
                ('highlighted_article_piece', models.CharField(blank=True, max_length=200)),
                ('comment', models.CharField(blank=True, max_length=200)),
                ('time_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('time_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='highlights', to='articles.Article')),
                ('highlighter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='highlights', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('time_updated',),
            },
        ),
        migrations.CreateModel(
            name='LikesDislikes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes', models.BooleanField()),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like', to='articles.Article')),
                ('reader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Article')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='likesdislikes',
            unique_together={('article', 'reader')},
        ),
    ]
