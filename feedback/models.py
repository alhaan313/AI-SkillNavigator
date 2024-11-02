from django.db import models
from django.contrib.auth.models import User

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    
    # Questions about courses, tests, and the website
    course_quality = models.IntegerField(choices=[
        (1, '1 - Worst'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent')
    ])
    test_quality = models.IntegerField(choices=[
        (1, '1 - Worst'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent')
    ])
    website_experience = models.IntegerField(choices=[
        (1, '1 - Worst'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent')
    ])
    additional_feedback = models.TextField(blank=True, null=True)  # Optional feedback

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username} on {self.created_at}"
