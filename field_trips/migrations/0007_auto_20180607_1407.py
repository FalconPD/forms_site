# Generated by Django 2.0.5 on 2018-06-07 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field_trips', '0006_auto_20180603_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldtrip',
            name='log_text',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='adminoptions',
            name='window_open',
            field=models.BooleanField(default=False, verbose_name='Accepting requests'),
        ),
    ]
