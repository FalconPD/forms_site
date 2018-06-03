from django.urls import path

from . import views

app_name = 'field_trips'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.detail, name='detail'),
    path('calendar', views.calendar, name='calendar'),
    path('create', views.create, name='create'),
    path('approve', views.approve_index, name='approve_index'),
    path('approve/<int:pk>', views.approve, name='approve'),
    path('admin', views.admin_index, name='admin_index'),
]
