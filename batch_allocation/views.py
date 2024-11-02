# batch/views.py
from django.shortcuts import render, get_object_or_404
from .models import Batch
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import allocate_batch, generate_content

@login_required
def batch_enrollment_view(request):
    # Allocate batch for the user
    status, batch = allocate_batch(request.user)

    # Check the allocation status and display the appropriate message
    if status == "enrolled":
        messages.success(request, f"You have been allocated to the {batch.name}.")
    elif status == "already_enrolled":
        messages.info(request, f"You are already enrolled in the {batch.name}.")
    else:
        messages.error(request, "No suitable batch available or batch is full.")

    return render(request, 'batch_allocation/batch_enrollment.html', {
        'batch': batch,
    })

@login_required
def course_page(request, batch_id):
    # Fetch the batch and its topics
    batch = get_object_or_404(Batch, id=batch_id)
    topics = batch.topics.all()

    # Default topic material
    selected_topic = request.GET.get('topic', None)  # Get the selected topic, default to None
    material = None
    
    if selected_topic:
        # Generate learning material based on the selected topic
        material = generate_content(selected_topic)  # Function to generate content

    context = {
        'batch': batch,
        'topics': topics,
        'selected_topic': selected_topic,
        'material': material,
    }

    # Render only the content part for AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'batch_allocation/partial_material.html', context)
    
    # Render full page for non-AJAX requests
    return render(request, 'batch_allocation/course_page.html', context)
