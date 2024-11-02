# profile/admin.py
from django.contrib import admin
from .models import Profile, Course, Internship, Certification

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'degree', 'specialization', 'phone_number')
    search_fields = ('user__username', 'name', 'email')
    
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'platform', 'certificate')
    search_fields = ('user__username', 'name', 'platform')
    list_filter = ('user',)

@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'company', 'start_date', 'end_date', 'certificate')
    search_fields = ('user__username', 'title', 'company')
    list_filter = ('user',)

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'certificate')
    search_fields = ('user__username', 'name')
    list_filter = ('user',)
