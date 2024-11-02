# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from batch_allocation.models import Batch

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/signup.html')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists, please choose a different one')
            return render(request, 'accounts/signup.html')

        # Create the user if the username is unique
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, 'Account created successfully')
        return redirect('login')

    return render(request, 'accounts/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # redirect to home page or dashboard
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    # Get the user's batches
    user_batches = request.user.batches.all()  # This gets all batches associated with the user

    # If the user has any batches, select the first one (or apply your own logic)
    if user_batches.exists():
        batch = user_batches.first()  # You can modify this logic as needed
    else:
        batch = None  # Handle the case where the user has no batches

    return render(request, 'accounts/home.html', {'batch': batch})