# profiles/urls.py
from django.urls import path
from .views import update_profile_view, profile_view, delete_course, delete_internship, delete_certification, ProtectedProfileView

urlpatterns = [
    path('', profile_view, name='profile'),
    path('protected/', ProtectedProfileView.as_view(), name='protected_profile'),
    path('update', update_profile_view, name='update_profile'),
    path('delete_course/<int:course_id>/', delete_course, name='delete_course'),
    path('delete_internship/<int:internship_id>/', delete_internship, name='delete_internship'),
    path('delete_certification/<int:certification_id>/', delete_certification, name='delete_certification'),
]
