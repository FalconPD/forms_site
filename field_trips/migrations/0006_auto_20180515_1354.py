# Generated by Django 2.0.5 on 2018-05-15 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field_trips', '0005_auto_20180515_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approval',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='approval',
            name='timestamp',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='nurse_comments',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='nurse_name',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='transportation_comments',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='transported_by',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
