# Generated by Django 3.2.5 on 2022-03-23 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20220322_1113'),
    ]

    operations = [
        migrations.CreateModel(
            name='CachedListHotels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keywordHash', models.CharField(default=None, max_length=32, null=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.city')),
                ('hotels', models.ManyToManyField(default=None, to='api.Hotel')),
            ],
        ),
    ]