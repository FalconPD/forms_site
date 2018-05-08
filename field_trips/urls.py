from django.urls import path

from . import views

app_name = 'field_trips'
urlpatterns = [
    path('create', views.create, name='create'),
]
