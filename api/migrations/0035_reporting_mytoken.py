# Generated by Django 3.2.4 on 2022-06-06 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_linktomanager'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporting',
            name='mytoken',
            field=models.CharField(default='', max_length=500),
            preserve_default=False,
        ),
    ]
