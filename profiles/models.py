from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    PROGRAMMING_LANGUAGES = [
        ('Python', 'Python'),
        ('.Net', '.Net'),
        ('Java', 'Java'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    degree = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    linkedin_profile = models.URLField(blank=True, null=True)
    github_profile = models.URLField(blank=True, null=True)
    programming_languages = models.CharField(
        max_length=7,
        choices=PROGRAMMING_LANGUAGES,
        help_text="Choose a programming language",
    )

    def __str__(self):
        return self.user.username

class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=200)
    certificate = models.FileField(upload_to='certificates/courses/', blank=True, null=True)  # Optional PDF upload
    
    class Meta:
        unique_together = (('user', 'name', 'platform'),)

class Internship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    start_date = models.DateField(default=timezone.now)  # Set default to current date
    end_date = models.DateField(default=timezone.now) 
    certificate = models.FileField(upload_to='certificates/internships/', blank=True, null=True)  # Optional PDF upload
    
    class Meta:
        unique_together = (('user', 'title', 'company', 'start_date'),)

class Certification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True)
    certificate = models.FileField(upload_to='certificates/certifications/', blank=True, null=True)  # Optional PDF upload

    class Meta:
        unique_together = (('user', 'name'),)