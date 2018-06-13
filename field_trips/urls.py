from django.urls import path

from . import views

app_name = 'field_trips'
urlpatterns = [
    path('', views.index, name='index'),
    path('list/<int:status>', views.list, name='list'),
    path('<int:pk>/', views.detail, name='detail'),
    path('calendar', views.calendar, name='calendar'),
    path('create', views.create, name='create'),
    path('approve', views.approve_index, name='approve_index'),
    path('approve/<int:pk>', views.approve, name='approve'),
    path('admin', views.admin_index, name='admin_index'),
    path('admin/<int:pk>', views.admin_detail, name='admin_detail'),
    path('admin/action', views.admin_action, name='admin_action'),
    path('admin/list/<int:status>', views.admin_list, name='admin_list'),
]
