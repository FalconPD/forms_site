# Generated by Django 2.0.5 on 2018-05-17 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('field_trips', '0011_approval_building'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approval',
            name='building',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='field_trips.Building'),
        ),
    ]
