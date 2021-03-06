# Generated by Django 3.2.5 on 2022-03-16 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_hotelreview_restaurantreview'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotel',
            name='lastFetchedReviews',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='hotel',
            name='reviews',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='lastFetchedReviews',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='reviews',
            field=models.TextField(default=None, null=True),
        ),
    ]
