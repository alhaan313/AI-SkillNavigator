from django import forms
from .models import Profile, Course, Internship, Certification
from django import forms

class ProfileForm(forms.ModelForm):
    PROGRAMMING_LANGUAGE_CHOICES = [
        ('Python', 'Python'),
        ('.Net', '.NET'),
        ('Java', 'Java'),
    ]

    programming_languages = forms.ChoiceField(
        choices=PROGRAMMING_LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})  # Add Bootstrap class for styling
    )

    class Meta:
        model = Profile
        fields = [
            'name', 'email', 'degree', 'specialization', 'phone_number',
            'linkedin_profile', 'github_profile', 'programming_languages'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Degree'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specialization'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'linkedin_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn Profile'}),
            'github_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'GitHub Profile'}),
            # 'programming_languages' field is now handled above with a ChoiceField
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'platform', 'certificate']  # Include the certificate field
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Name'}),
            'platform': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Platform'}),
            'certificate': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload Certificate (PDF)'}),  # PDF upload field
        }

class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = ['title', 'company', 'start_date', 'end_date', 'certificate']  # Include the certificate field
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Internship Title'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Start Date', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'End Date', 'type': 'date'}),
            'certificate': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload Certificate (PDF)'}),  # PDF upload field
        }

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'certificate']  # Include the certificate field
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Certification Name'}),
            'certificate': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload Certificate (PDF)'}),  # PDF upload field
        }