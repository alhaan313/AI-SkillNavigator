# test/models.py
from django.db import models
from django.contrib.auth.models import User
from batch_allocation.models import Batch  # Ensure Batch model is in a separate app

class TestTopic(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="topics")
    topic_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.topic_name} ({self.batch.name})"
 
class UserScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(TestTopic, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    attempts = models.IntegerField(default=0)
    last_attempted = models.DateTimeField(auto_now=True)  # Automatically updated with each attempt
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)  # Add this line


    class Meta:
        unique_together = ('user', 'topic')  # Ensure one score per user-topic combination

    def __str__(self):
        return f"{self.user.username} - {self.topic.topic_name} - Score: {self.score}, Attempts: {self.attempts}"