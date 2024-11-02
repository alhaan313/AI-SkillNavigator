from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile, Course, Internship, Certification
from .forms import ProfileForm, CourseForm, InternshipForm, CertificationForm
from datetime import datetime
from django.utils import timezone
import os

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

class ProtectedProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'This is a protected profile view!'}
        return Response(content)

@login_required
def profile_view(request):
    try:
        profile = Profile.objects.get(user=request.user)

        # Fetch related courses, internships, and certifications
        courses = Course.objects.filter(user=request.user)
        internships = Internship.objects.filter(user=request.user)
        certifications = Certification.objects.filter(user=request.user)

        return render(request, 'profiles/profile.html', {
            'profile': profile,
            'courses': courses,
            'internships': internships,
            'certifications': certifications,
        })
    except Profile.DoesNotExist:
        return redirect('update_profile')


@login_required
def update_profile_view(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)  # Create a new Profile instance but don't save yet

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)

        # Save profile details if valid
        if profile_form.is_valid():
            profile_form.save()  # Save the profile instance

            # Process multiple courses
            i = 0
            while True:
                name = request.POST.get(f'courses[{i}][name]')
                platform = request.POST.get(f'courses[{i}][platform]')
                certificate = request.FILES.get(f'courses[{i}][certificate]')

                if name is None and platform is None and certificate is None:
                    break  # Stop if no more courses are found

                if name and platform:  # Check if name and platform are provided
                    # Check if the course already exists
                    course, created = Course.objects.get_or_create(
                        user=request.user,
                        name=name,
                        platform=platform,
                    )
                    if created:  # If a new course was created, set the certificate
                        course.certificate = certificate
                        course.save()

                i += 1

            # Process multiple internships
            j = 0
            while True:
                title = request.POST.get(f'internships[{j}][title]')
                company = request.POST.get(f'internships[{j}][company]')
                start_date = request.POST.get(f'internships[{j}][start_date]')
                end_date = request.POST.get(f'internships[{j}][end_date]')
                certificate = request.FILES.get(f'internships[{j}][certificate]')

                if title is None and company is None and start_date is None and end_date is None and certificate is None:
                    break  # Stop if no more internships are found

                if title and company:  # Check if title and company are provided
                    try:
                        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else timezone.now().date()
                        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else timezone.now().date()
                    except ValueError:
                        start_date = end_date = timezone.now().date()  # Use today's date if parsing fails

                    # Check if the internship already exists
                    internship, created = Internship.objects.get_or_create(
                        user=request.user,
                        title=title,
                        company=company,
                        start_date=start_date,
                        end_date=end_date,
                    )
                    if created:  # If a new internship was created, set the certificate
                        internship.certificate = certificate
                        internship.save()

                j += 1

            # Process multiple certifications
            k = 0
            while True:
                name = request.POST.get(f'certifications[{k}][name]')
                certificate = request.FILES.get(f'certifications[{k}][certificate]')

                if name is None and certificate is None:
                    break  # Stop if no more certifications are found

                if name:  # Check if name is provided
                    # Check if the certification already exists
                    certification, created = Certification.objects.get_or_create(
                        user=request.user,
                        name=name,
                    )
                    if created:  # If a new certification was created, set the certificate
                        certification.certificate = certificate
                        certification.save()

                k += 1

            return redirect('profile')  # Redirect to profile after saving

        else:
            print("Profile form errors:", profile_form.errors)  # Log errors if the form is not valid

    else:
        profile_form = ProfileForm(instance=profile)  # Pass the profile instance

    # Retrieve all related objects to display in the form
    courses = Course.objects.filter(user=request.user)
    internships = Internship.objects.filter(user=request.user)
    certifications = Certification.objects.filter(user=request.user)

    return render(request, 'profiles/update_profile.html', {
        'profile_form': profile_form,
        'courses': courses,
        'internships': internships,
        'certifications': certifications,
    })


from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def delete_course(request, course_id):
    course = Course.objects.get(id=course_id)
    if course.user == request.user:
        if course.certificate:
            file_path = course.certificate.path
            if os.path.isfile(file_path):
                os.remove(file_path) 
        course.delete()
    return HttpResponseRedirect(reverse('profile'))

@login_required
def delete_internship(request, internship_id):
    internship = Internship.objects.get(id=internship_id)
    if internship.user == request.user:
        if internship.certificate:
            file_path = internship.certificate.path
            if os.path.isfile(file_path):
                os.remove(file_path) 
        internship.delete()
    return HttpResponseRedirect(reverse('profile'))

@login_required
def delete_certification(request, certification_id):
    certification = Certification.objects.get(id=certification_id)
    if certification.user == request.user:
        if certification.certificate:
            file_path = certification.certificate.path
            if os.path.isfile(file_path):
                os.remove(file_path)
        certification.delete()
    return HttpResponseRedirect(reverse('profile'))
