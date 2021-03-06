# Generated by Django 3.2.5 on 2022-01-09 12:43

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('api', '0005_auto_20220106_1022'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotel',
            name='restaurant',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='api.restaurant'),
        ),
        migrations.RemoveField(
            model_name='hotel',
            name='tags',
        ),
        migrations.AddField(
            model_name='hotel',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='tags',
        ),
        migrations.AddField(
            model_name='restaurant',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
