from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['course_quality', 'test_quality', 'website_experience', 'additional_feedback']
        widgets = {
            'course_quality': forms.Select(attrs={'class': 'form-select'}),
            'test_quality': forms.Select(attrs={'class': 'form-select'}),
            'website_experience': forms.Select(attrs={'class': 'form-select'}),
            'additional_feedback': forms.Textarea(attrs={
                'class': 'form-control',  # Bootstrap class for styling
                'rows': 4,
                'placeholder': 'Enter any additional feedback here...',
                'aria-label': 'Additional Feedback',  # Accessibility improvement
            }),
        }
