# Generated by Django 3.2.4 on 2022-06-17 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0038_locationrecommendations_customer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='getkeywordthemesrecommendations',
            name='mytoken',
            field=models.CharField(default='', max_length=500),
            preserve_default=False,
        ),
    ]
