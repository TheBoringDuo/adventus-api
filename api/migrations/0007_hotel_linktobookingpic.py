# Generated by Django 3.2.5 on 2022-02-18 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20220109_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotel',
            name='linkToBookingPic',
            field=models.TextField(default='', null=True),
        ),
    ]