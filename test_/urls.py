# test/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('generate_report_pdf/', views.generate_report_pdf, name='generate_report_pdf'),
    path('<int:batch_id>/', views.generate_test, name='generate_test'),
    path('<int:batch_id>/<str:selected_topic>', views.generate_topic_test, name='generate_topic_test'),
    path('toppers/', views.topper_view, name='topper_page'),
    path('submit_test/', views.submit_test, name='submit_test'),
    path('success/', views.success_page, name='success_page'),
]
