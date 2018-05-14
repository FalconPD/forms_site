# forms_site
Trying to create a django site for district forms

## Starting a New Database
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata field_trips/fixtures/*
python manage.py createsuperuser
```
Sign in to the admin site and setup SSO
Keys: https://apps.dev.microsoft.com
