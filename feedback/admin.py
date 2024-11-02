# feedback/admin.py
from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'course_quality', 'test_quality', 'website_experience', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('course_quality', 'test_quality', 'website_experience', 'created_at')
    ordering = ('-created_at',)  # Order by the most recent feedback

    def has_change_permission(self, request, obj=None):
        return False  # 
