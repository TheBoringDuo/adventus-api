# Generated by Django 3.2.5 on 2022-03-18 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_alter_searchphrase_phrase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchphrase',
            name='phrase',
            field=models.TextField(max_length=100, unique=True),
        ),
    ]