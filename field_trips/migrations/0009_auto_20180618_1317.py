# Generated by Django 2.0.6 on 2018-06-18 17:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('field_trips', '0008_auto_20180609_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldtrip',
            name='anticipatory',
            field=models.TextField(blank=True, help_text='To be completed with students in advance of trip', verbose_name='Description of Anticipatory Activity'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='building',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='field_trips.Building'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='buses',
            field=models.IntegerField(blank=True, help_text='Each bus seats 52 people.', verbose_name='Number of Buses Required'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='costs',
            field=models.TextField(blank=True, help_text='Please describe all costs in detail. Buses are $75 per hour.'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='departing',
            field=models.DateTimeField(blank=True, verbose_name='Date and Time of Departure'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='destination',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='directions',
            field=models.FileField(blank=True, upload_to='field_trips/'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='discipline',
            field=models.ForeignKey(blank=True, help_text='Used to select supervisor for approval', on_delete=django.db.models.deletion.CASCADE, to='field_trips.Discipline', verbose_name='Discipline'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='funds',
            field=models.CharField(blank=True, choices=[('BUILDING', 'Building Budget'), ('STUDENT', 'Student Funded')], max_length=8, verbose_name='Source of Funds'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='grades',
            field=models.ManyToManyField(blank=True, to='field_trips.Grade'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='group',
            field=models.CharField(blank=True, max_length=64, verbose_name='Class / Group / Club'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='itinerary',
            field=models.TextField(blank=True, help_text='Please include time at destination, lunch arrangements, and additional stops.'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='pupils',
            field=models.IntegerField(blank=True, null=True, verbose_name='Number of Pupils'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='purpose',
            field=models.TextField(blank=True, help_text='What will the students learn, and HOW?', verbose_name='Description of Educational Value of Trip'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='returning',
            field=models.DateTimeField(blank=True, verbose_name='Date and Time Returning to School'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='roster',
            field=models.FileField(blank=True, upload_to='field_trips/'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='standards',
            field=models.TextField(blank=True, help_text='Please be specific.', verbose_name='Unit(s) of Study / Curriculum Standards Addressed During Trip'),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='status',
            field=models.IntegerField(choices=[(0, 'Archived'), (1, 'In Progress'), (2, 'Approved'), (3, 'Denied'), (4, 'Dropped'), (5, 'Draft'), (6, 'Pending Board Approval')], default=1),
        ),
        migrations.AlterField(
            model_name='fieldtrip',
            name='teachers',
            field=models.IntegerField(blank=True, null=True, verbose_name='Number of Teachers'),
        ),
    ]
