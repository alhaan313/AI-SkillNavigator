# batch_allocation/utils.py

from .models import Batch
import google.generativeai as genai
import markdown
from bs4 import BeautifulSoup

genai.configure(api_key="Your API key")

def allocate_batch(user):
    languages = [lang.strip().lower() for lang in user.profile.programming_languages.split(',')]
    batch = None

    # Check which batch to allocate based on programming languages
    if 'java' in languages:
        batch = Batch.objects.filter(name='Java Batch').first()
    elif '.net' in languages:
        batch = Batch.objects.filter(name='.NET Batch').first()
    elif 'python' in languages:
        batch = Batch.objects.filter(name='Data Engineering Batch').first()

    # Check if the batch can accept more candidates
    if batch:
        # Check if the user is already in the batch
        if batch.candidates.filter(id=user.id).exists():
            return "already_enrolled", batch  # Return a specific message for existing enrollment

        if batch.current_candidates < batch.max_candidates:
            batch.current_candidates += 1  # Increment the current candidate count
            batch.candidates.add(user)  # Add user to the batch
            batch.save()  # Save the updated batch
            return "enrolled", batch

    return "no_batch", None


def md_to_text(md):
    # Convert Markdown to HTML
    html = markdown.markdown(md)
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, features='html.parser')
    
    # Optionally add custom styles or classes
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        heading['class'] = 'my-heading-class'  # Add a custom CSS class for styling
    
    # Return the prettified HTML
    return soup.prettify()  # Use prettify() for better formatting (optional)

def generate_content(topic):
    ask = f"Provide a detailed explanation about the topic '{topic}'."
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(ask)
        
        # Get the generated text
        generated_text = response.text
        
        # Convert the generated text to Markdown format
        beautiful_content = md_to_text(generated_text)
        return beautiful_content
    except Exception as e:
        print(f"Error generating content: {e}")
        return "Content generation unavailable at the moment."



