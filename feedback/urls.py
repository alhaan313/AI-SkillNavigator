from django.urls import path
from .views import feedback_view, feedback_summary_view

urlpatterns = [
    path('', feedback_view, name='feedback'),
    path('summary/', feedback_summary_view, name='feedback_summary'),

]
