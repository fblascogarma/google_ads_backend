# Generated by Django 3.2.4 on 2021-12-07 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_getkeywordthemesrecommendations_geo_target_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='getbudgetrecommendations',
            name='business_location_id',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='getbudgetrecommendations',
            name='business_name',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
