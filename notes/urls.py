from django.urls import path
from . import views

urlpatterns = [
    path('', views.list, name='list'),
    path('Content', views.content, name='Content'),
    path('Create', views.CreateText, name='Create'),
]