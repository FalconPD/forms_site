# Generated by Django 2.0.5 on 2018-05-18 16:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Approval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approved', models.NullBooleanField(verbose_name='Do you approve this field trip?')),
                ('comments', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Approver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('name', models.CharField(max_length=64)),
                ('title', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('code', models.CharField(max_length=8)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Chaperone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('phone_number', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='FieldTrip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='In Progress', max_length=64)),
                ('submitted', models.DateTimeField(auto_now_add=True, verbose_name='Submitted')),
                ('destination', models.CharField(max_length=64)),
                ('group', models.CharField(max_length=64, verbose_name='Class / Group / Club')),
                ('roster', models.FileField(upload_to='field_trips/')),
                ('itinerary', models.TextField(help_text='Please include time at destination, lunch arrangements, and additional stops.')),
                ('pupils', models.IntegerField(verbose_name='Number of Pupils')),
                ('teachers', models.IntegerField(verbose_name='Number of Teachers')),
                ('departing', models.DateTimeField(verbose_name='Date and Time of Departure')),
                ('returning', models.DateTimeField(verbose_name='Date and Time Returning to School')),
                ('directions', models.FileField(upload_to='field_trips/')),
                ('buses', models.IntegerField(help_text='Each bus seats 52 people.', verbose_name='Number of Buses Required')),
                ('transported_by', models.CharField(blank=True, max_length=64)),
                ('transportation_comments', models.TextField(blank=True)),
                ('costs', models.TextField(help_text='Please describe all costs in detail. Buses are $75 per hour.')),
                ('funds', models.CharField(choices=[('BUILDING', 'Building Budget'), ('STUDENT', 'Student Funded')], max_length=8, verbose_name='Source of Funds')),
                ('standards', models.TextField(help_text='Please be specific.', verbose_name='Unit(s) of Study / Curriculum Standards Addressed During Trip')),
                ('anticipatory', models.TextField(help_text='To be completed with students in advance of trip', verbose_name='Description of Anticipatory Activity')),
                ('purpose', models.TextField(help_text='What will the students learn, and HOW?', verbose_name='Description of Educational Value of Trip')),
                ('nurse_required', models.NullBooleanField()),
                ('nurse_comments', models.TextField(blank=True)),
                ('nurse_name', models.CharField(blank=True, max_length=64)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='field_trips.Building')),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('code', models.CharField(max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.AddField(
            model_name='fieldtrip',
            name='extra_vehicles',
            field=models.ManyToManyField(blank=True, to='field_trips.Vehicle', verbose_name='Additional Vehicles Required'),
        ),
        migrations.AddField(
            model_name='fieldtrip',
            name='grades',
            field=models.ManyToManyField(to='field_trips.Grade'),
        ),
        migrations.AddField(
            model_name='fieldtrip',
            name='submitter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='fieldtrip',
            name='supervisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='field_trips.Approver', verbose_name='Approving Supervisor'),
        ),
        migrations.AddField(
            model_name='chaperone',
            name='field_trip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='field_trips.FieldTrip'),
        ),
        migrations.AddField(
            model_name='approver',
            name='buildings',
            field=models.ManyToManyField(to='field_trips.Building'),
        ),
        migrations.AddField(
            model_name='approver',
            name='roles',
            field=models.ManyToManyField(to='field_trips.Role'),
        ),
        migrations.AddField(
            model_name='approval',
            name='approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='field_trips.Approver'),
        ),
        migrations.AddField(
            model_name='approval',
            name='building',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='field_trips.Building'),
        ),
        migrations.AddField(
            model_name='approval',
            name='field_trip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='field_trips.FieldTrip'),
        ),
        migrations.AddField(
            model_name='approval',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='field_trips.Role'),
        ),
    ]
