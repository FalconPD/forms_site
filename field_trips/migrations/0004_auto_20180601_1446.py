# Generated by Django 2.0.5 on 2018-06-01 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('field_trips', '0003_auto_20180601_1323'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fieldtrip',
            name='supervisor',
        ),
        migrations.AddField(
            model_name='fieldtrip',
            name='discipline',
            field=models.ForeignKey(default=0, help_text='Used to select supervisor for approval', on_delete=django.db.models.deletion.CASCADE, to='field_trips.Discipline', verbose_name='Discipline'),
            preserve_default=False,
        ),
    ]
