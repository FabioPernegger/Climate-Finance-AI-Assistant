from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('delete-topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    path('discovery/', views.discovery_page, name='discovery'),
    #path('discovery/<int:queryid>/', views.discovery_page, name='discovery'),
    path('report/<int:report_id>/', views.report_page, name='report'),
    path('generate-demo-data/', views.generate_demo_data_view, name='generate_demo_data'),
    path('monitor-question/', views.monitor_question, name='monitor_question'),
]