# Generated by Django 2.1.4 on 2019-04-17 01:48

from django.db import migrations, models
import doll_sites.models


class Migration(migrations.Migration):

    dependencies = [
        ('doll_sites', '0006_auto_20190307_1610'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlideBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner_pic', models.ImageField(upload_to=doll_sites.models.banner_upload_location)),
                ('banner_title', models.CharField(max_length=999)),
                ('banner_link', models.CharField(max_length=999)),
            ],
        ),
        migrations.AddField(
            model_name='actress',
            name='count_album',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='actress',
            name='hot_search',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='actress',
            name='temperature',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='photo',
            name='history_views_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='photo',
            name='suited_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='photo',
            name='temperature',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='photo',
            name='video_link',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='video_poster',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='yesterday_views_count',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]
