# batch/urls.py
from django.urls import path
from .views import batch_enrollment_view, course_page

urlpatterns = [
    path('enroll/', batch_enrollment_view, name='batch_enrollment'),
    path('<int:batch_id>/course/', course_page, name='course_page')

]
