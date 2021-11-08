# Generated by Django 3.2.5 on 2021-10-30 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20211030_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='destID',
            field=models.CharField(max_length=12, unique=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.city'),
        ),
        migrations.AlterUniqueTogether(
            name='city',
            unique_together={('name', 'country')},
        ),
    ]