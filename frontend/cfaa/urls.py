from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('discovery/', views.discovery_page, name='discovery'),
    #path('discovery/<int:queryid>/', views.discovery_page, name='discovery'),
    path('report/<int:report_id>/', views.report_page, name='report'),
    path('monitor-question/', views.monitor_question, name='monitor_question'),
]