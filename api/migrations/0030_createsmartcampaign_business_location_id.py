# Generated by Django 3.2.4 on 2022-02-05 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_editkeywordthemes'),
    ]

    operations = [
        migrations.AddField(
            model_name='createsmartcampaign',
            name='business_location_id',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]