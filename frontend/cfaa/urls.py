from django.urls import path
from . import views

urlpatterns = [
    path('', views.discovery_page, name='discovery'),
    path('report/', views.report_page, name='report'),
]