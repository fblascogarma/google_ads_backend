# Generated by Django 3.2.4 on 2021-08-31 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_googleadsaccountcreation_mytoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewAccountCustomerID',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mytoken', models.CharField(max_length=500)),
                ('customer_id', models.CharField(max_length=500)),
            ],
        ),
    ]
