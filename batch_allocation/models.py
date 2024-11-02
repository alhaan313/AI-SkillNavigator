# models.py
from django.db import models
from django.contrib.auth.models import User


class Batch(models.Model):
    name = models.CharField(max_length=100)
    programming_languages = models.CharField(max_length=255)
    min_candidates = models.PositiveIntegerField(default=25)
    max_candidates = models.PositiveIntegerField(default=30)
    current_candidates = models.PositiveIntegerField(default=0)  # Track the number of candidates
    candidates = models.ManyToManyField(User, related_name='batches')  # Relationship with User

    def __str__(self):
        return self.name
