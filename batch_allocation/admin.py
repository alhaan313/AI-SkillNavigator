# batch_allocation/admin.py
from django.contrib import admin
from .models import Batch

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'programming_languages', 'min_candidates', 'max_candidates', 'current_candidates')
    search_fields = ('name', 'programming_languages')
    list_filter = ('min_candidates', 'max_candidates')
    ordering = ('name',)  # Order by name

    def candidate_count(self, obj):
        return obj.candidates.count()
    candidate_count.short_description = 'Number of Candidates'
