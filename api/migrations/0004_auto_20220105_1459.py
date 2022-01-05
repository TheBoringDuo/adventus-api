# Generated by Django 3.2.5 on 2022-01-05 14:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_user_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hotel',
            name='link',
        ),
        migrations.AddField(
            model_name='hotel',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='hotel',
            name='available',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='hotel',
            name='bookingLink',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='hotel',
            name='description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='hotel',
            name='isFetchedFromBooking',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='hotel',
            name='listed',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='hotel',
            name='locLat',
            field=models.DecimalField(decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='hotel',
            name='locLong',
            field=models.DecimalField(decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='hotel',
            name='ownedBy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('available', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True)),
                ('listed', models.BooleanField(default=True)),
                ('locLong', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('locLat', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.city')),
                ('ownedBy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]