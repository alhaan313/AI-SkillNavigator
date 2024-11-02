# test/admin.py
from django.contrib import admin
from .models import TestTopic, UserScore

@admin.register(TestTopic)
class TestTopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch', 'topic_name')
    search_fields = ('topic_name',)
    list_filter = ('batch',)

@admin.register(UserScore)
class UserScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'topic', 'score', 'attempts', 'last_attempted')
    search_fields = ('user__username', 'topic__topic_name')
    list_filter = ('user', 'topic')

