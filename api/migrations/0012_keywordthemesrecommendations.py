# Generated by Django 3.2.4 on 2021-08-03 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_reporting'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeywordThemesRecommendations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refreshToken', models.CharField(max_length=500)),
                ('keyword_text', models.CharField(max_length=500)),
                ('country_code', models.CharField(max_length=500)),
                ('language_code', models.CharField(max_length=500)),
            ],
        ),
    ]