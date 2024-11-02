# visualization/views.py
from django.shortcuts import render
from test_.models import UserScore
from django.contrib.auth.decorators import login_required
import json


@login_required
def results_view(request):
    # Logic to fetch user scores and prepare data for visualization
    return render(request, 'visual/results.html', {
        # Pass necessary data for visualization
    })

@login_required
def user_score_visualization(request):
    # Fetch user scores for the logged-in user
    user_scores = UserScore.objects.filter(user=request.user)
    
    # Prepare data for the charts
    topics = [score.topic.topic_name for score in user_scores]
    scores = [score.score for score in user_scores]
    attempts = [score.attempts for score in user_scores]
    last_attempted_dates = [score.last_attempted.strftime("%Y-%m-%d") for score in user_scores]

    context = {
        'topics': json.dumps(topics),           # Convert data to JSON for JavaScript
        'scores': json.dumps(scores),
        'attempts': json.dumps(attempts),
        'last_attempted_dates': json.dumps(last_attempted_dates),
    }
    
    return render(request, 'visual/user_score_visualization.html', context)

