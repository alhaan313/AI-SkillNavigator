from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FeedbackForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q


@login_required
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user  # Associate feedback with the logged-in user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('feedback')  # Redirect to the same feedback page or a thank you page
    else:
        form = FeedbackForm()
    
    return render(request, 'feedback/feedback.html', {'form': form})

from django.shortcuts import render
from .models import Feedback
from textblob import TextBlob
from django.contrib.auth.decorators import login_required

@login_required
def feedback_summary_view(request):
    feedbacks = Feedback.objects.all()
    
    # Initialize counters for each rating category
    total_course_quality = 0
    total_test_quality = 0
    total_website_experience = 0
    feedback_count = feedbacks.count()
    
    # Collect text feedback for sentiment analysis
    all_feedback_texts = []
    
    for feedback in feedbacks:
        total_course_quality += feedback.course_quality
        total_test_quality += feedback.test_quality
        total_website_experience += feedback.website_experience
        if feedback.additional_feedback:
            all_feedback_texts.append(feedback.additional_feedback)

    # Calculate average ratings
    avg_course_quality = total_course_quality / feedback_count if feedback_count else 0
    avg_test_quality = total_test_quality / feedback_count if feedback_count else 0
    avg_website_experience = total_website_experience / feedback_count if feedback_count else 0

    # Perform sentiment analysis on additional feedback
    combined_text = " ".join(all_feedback_texts)
    sentiment_analysis = TextBlob(combined_text).sentiment
    overall_sentiment = 'Positive' if sentiment_analysis.polarity > 0 else 'Negative' if sentiment_analysis.polarity < 0 else 'Neutral'
    
    feedback_list = Feedback.objects.exclude(Q(additional_feedback="") | Q(additional_feedback__isnull=True))

    # Render data to template
    context = {
        'avg_course_quality': avg_course_quality,
        'avg_test_quality': avg_test_quality,
        'avg_website_experience': avg_website_experience,
        'overall_sentiment': overall_sentiment,
        'sentiment_score': sentiment_analysis.polarity,
        'feedback_list': feedback_list,
    }
    
    return render(request, 'feedback/feedback_summary.html', context)
