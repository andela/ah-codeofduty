# Generated by Django 2.1.2 on 2018-11-12 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0006_highlight'),
    ]

    operations = [
        migrations.AddField(
            model_name='highlight',
            name='highlighted_article_piece',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
