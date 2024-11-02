# visualization/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('results/', views.results_view, name='results'),
    path('user_score_visualization/', views.user_score_visualization, name='user_score_visualization'),

]
