# test/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from . models import TestTopic, UserScore
from .utils import generate_mcq_question, Ai_course_recom, get_unique_image_links, generate_feedback, md_to_html, md_to_text
from batch_allocation.models import Batch

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import random
import logging

@login_required
def generate_test(request, batch_id):
    # Retrieve the batch and its topics
    batch = Batch.objects.get(id=batch_id)
    topics = list(batch.topics.all())

    # Select 10 random topics
    selected_topics = random.sample(topics, min(10, len(topics)))

    # Generate questions for each topic
    questions = []
    for topic in selected_topics:
        generated_question = generate_mcq_question(topic.topic_name)
        if generated_question:
            correct_answer = generated_question.get("correct_answer")
            if correct_answer is not None:
                questions.append({
                    "topic": topic.topic_name,
                    "question": generated_question["question"],
                    "options": generated_question["options"],  # A dictionary of options (A, B, C, D)
                    "correct_answer": correct_answer.strip(')')  # Store without closing parenthesis
                })
            else:
                # Log or handle the case where the correct answer is None
                print(f"Warning: No correct answer generated for topic: {topic.topic_name}")
        else:
            print(f"Warning: No question generated for topic: {topic.topic_name}")

    request.session['questions'] = questions  # Store in session for score calculation
    request.session['test_type'] = 'generate_test'  # Set flag for submit_test

    # Render questions on the test page
    return render(request, 'test_/generate_test.html', {
        'batch': batch,
        'questions': questions,
    })


def generate_topic_test(request, batch_id, selected_topic):
    """
    Generates a test with 10 questions on a single specified topic.
    """
    batch = get_object_or_404(Batch, id=batch_id)
    questions = []
    max_attempts, count, attempts = 20, 0, 0

    logging.debug(f"Starting question generation for topic: {selected_topic}")
    
    while count < 10 and attempts < max_attempts:
        generated_question = generate_mcq_question(selected_topic)
        attempts += 1

        if generated_question and generated_question.get("correct_answer"):
            questions.append({
                "topic": selected_topic,
                "question": generated_question["question"],
                "options": generated_question["options"],
                "correct_answer": generated_question["correct_answer"].strip(')')
            })
            count += 1
            logging.debug(f"Question {count} added for topic {selected_topic}")
        else:
            logging.warning(f"Attempt {attempts} failed to generate a valid question for topic: {selected_topic}")

    if count < 10:
        logging.warning(f"Only {count} questions generated after {attempts} attempts for topic {selected_topic}")

    # Save questions in the session
    request.session['questions'] = questions
    request.session['test_type'] = 'generate_topic_test'  # Set flag for submit_test

    return render(request, 'test_/generate_topic_test.html', {
        'batch': batch,
        'selected_topic' : selected_topic,
        'questions': questions,
    })


@login_required
def submit_test(request):
    if request.method == 'POST':
        questions = request.session.get('questions', [])
        test_type = request.session.get('test_type')  # Get the test type flag
        score = 0
        incorrect_questions = []  # Store incorrectly answered questions and correct answers
        incorrect_topics = []  # Track incorrect answers if needed
        total_questions = len(questions)  # Track total questions

        batch_id = request.POST.get('batch_id')  # Ensure this is sent in the POST request
        print(batch_id)
        # batch_id = int(batch_id)
        for index, question in enumerate(questions, start=1):
            submitted_answer = request.POST.get(f'answer_{index}')
            correct_answer = question.get('correct_answer')
            correct_answer_text = question["options"].get(correct_answer)  # Retrieve answer text
            correct_answer_text = correct_answer.lower() + ') ' + str(correct_answer_text)


            if submitted_answer and correct_answer:
                if submitted_answer[0] == correct_answer[0]:  # Correct answer
                    score += 1
                else:
                    # Track topic if the answer is incorrect
                    # Add incorrect question details
                    incorrect_questions.append({
                        "topic": question["topic"],
                        "question": question["question"],
                        "correct_answer": correct_answer_text,
                    })
                    # if test_type == 'generate_test':  # Only track for 'generate_test'
                    incorrect_topics.append(question["topic"])

        # Process score and attempts for each topic only if called from 'generate_topic_test'
        if test_type == 'generate_topic_test':
            unique_topics = set(question["topic"] for question in questions)
            for topic_name in unique_topics:
                logging.debug(f"Attempting to retrieve TestTopic for: {topic_name}")
                try:
                    topic = TestTopic.objects.get(topic_name=topic_name)

                    # Retrieve or create the UserScore entry for the topic
                    user_score, created = UserScore.objects.get_or_create(user=request.user, topic=topic, batch_id=batch_id)

                    # Update the attempt count only once per test
                    if created:
                        user_score.attempts = 1
                    else:
                        user_score.attempts += 1  # Increment the attempt count for this topic

                    # Update score only if the new score is higher than the previous score
                    user_score.score = max(user_score.score, score)
                    user_score.save()

                except TestTopic.DoesNotExist:
                    logging.error(f"TestTopic with name {topic_name} does not exist.")
                    # Handle the case where the topic does not exist
                    continue  # Skip to the next topic or handle it as needed

        # Store the score and incorrect topics in the session, then clear questions
        request.session['score'] = score
        request.session['total_questions'] = total_questions  # Store total questions in session
        request.session['incorrect_questions'] = incorrect_questions

        
        request.session['incorrect_topics'] = list(set(incorrect_topics))  # Save incorrect topics if needed

        # Redirect to the success page
        return redirect('success_page')


@login_required
def success_page(request):
    user_scores = UserScore.objects.filter(user=request.user)
    test_type = request.session.pop('test_type', None)  # Get the test type from the session
    score = request.session.pop('score', 0)  # Retrieve and remove score from session
    total_questions = request.session.pop('total_questions', 0)  # Retrieve and remove total questions from session
    incorrect_topics = request.session.pop('incorrect_topics', [])  # Retrieve and remove incorrect topics from session
    recommended_courses = Ai_course_recom(incorrect_topics)
    incorrect_questions = request.session.pop('incorrect_questions', [])
    selected_links = get_unique_image_links(len(recommended_courses))

    # Store values back in the session for the PDF generation
    request.session['pdf_score'] = score
    request.session['pdf_total_questions'] = total_questions
    request.session['pdf_incorrect_topics'] = incorrect_topics
    request.session['pdf_test_type'] = test_type

    # Combine recommended courses and image links
    combined_courses = [
        {
            'course': course,
            'image_link': selected_links[i]
        }
        for i, course in enumerate(recommended_courses)
    ]

    return render(request, 'test_/success_page.html', {
        'score': score,
        'total_questions': total_questions,  # Pass total questions to the template
        'test_type': test_type,  # Pass test type to the template
        'user_scores': user_scores,
        'incorrect_topics': incorrect_topics,  # Pass incorrect topics to the template
        'incorrect_questions': incorrect_questions,
        'recommended_courses': recommended_courses,  # Pass the recommended courses to the template
        'selected_links': selected_links,  # Pass the selected links to the template
        'combined_courses': combined_courses,  # Pass the combined courses to the template


    })


# views.py
from django.shortcuts import render
from django.db.models import Max
from .models import UserScore, TestTopic
from batch_allocation.models import Batch

def topper_view(request):
    selected_batch_id = request.GET.get('batch')
    selected_topic_id = request.GET.get('topic')

    # Fetch batches and topics for dropdown filters
    batches = Batch.objects.all()
    topics = TestTopic.objects.all()

    # Filter by selected batch and topic, if specified
    if selected_batch_id:
        batch = Batch.objects.get(id=selected_batch_id)
        topics = topics.filter(batch=batch)  # Only topics for the selected batch
        scores = UserScore.objects.filter(topic__batch=batch)
    else:
        scores = UserScore.objects.all()

    if selected_topic_id:
        topic = TestTopic.objects.get(id=selected_topic_id)
        scores = scores.filter(topic=topic)

    # Get top 10 scores per batch, with topic info
    top_scorers = []
    if selected_batch_id:
        scores = scores.order_by('-score', 'attempts')[:10]
        for score in scores:
            top_scorers.append({
                'user': score.user.username,
                'score': score.score,
                'attempts': score.attempts,
                'topic': score.topic.topic_name,
                'batch': score.topic.batch.name,
                'last_attempted': score.last_attempted,
            })
    else:
        for batch in batches:
            batch_scores = scores.filter(topic__batch=batch).order_by('-score', 'attempts')[:10]
            top_scorers += [{
                'user': score.user.username,
                'score': score.score,
                'attempts': score.attempts,
                'topic': score.topic.topic_name,
                'batch': batch.name,
                'last_attempted': score.last_attempted,
            } for score in batch_scores]

    return render(request, 'test_/topper_page.html', {
        'batches': batches,
        'topics': topics,
        'top_scorers': top_scorers,
        'selected_batch_id': selected_batch_id,
        'selected_topic_id': selected_topic_id,
    })
































from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
from django.contrib import messages
import io
import numpy as np
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def generate_report_pdf(request):
    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{request.user.username}_report.pdf"'

        # Initialize PDF structure with SimpleDocTemplate
        pdf = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(name='TitleStyle', fontSize=18, leading=22, spaceAfter=10, alignment=1)
        section_header_style = ParagraphStyle(name='SectionHeader', fontSize=14, leading=16, spaceAfter=8, textColor=colors.blue)
        body_text_style = styles['BodyText']

        username = request.user.username if request.user.is_authenticated else "Guest"

        # Add content to the PDF
        add_title_and_date(elements, request.user.username, title_style, body_text_style)
        add_performance_summary(elements, request, section_header_style, body_text_style)
        add_topic_analysis(elements, request, section_header_style, body_text_style)
        add_incorrect_questions_table(elements, request, section_header_style, body_text_style)
        add_recommended_next_steps(elements, request, section_header_style, body_text_style)

        # Insert Charts into the PDF
        add_charts(elements, request)

        # Build the PDF
        pdf.build(elements)
        return response

    except Exception as e:
        # Handle errors and add a message to be shown on the website
        # messages.error(request, f"An error occurred while generating the PDF: {str(e)}")
        # Return a simple HTML response to indicate an error occurred
        return HttpResponse("<h1>You have reloaded the page</h1><h2>An error occurred while generating the PDF. <br> Please write the test again and generate the report</h2>")


def add_title_and_date(elements, username, title_style, body_text_style):
    elements.append(Paragraph(f"Student Report for {username}", title_style))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_text_style))
    elements.append(Spacer(1, 0.2 * inch))


def add_performance_summary(elements, request, section_header_style, body_text_style):
    score = request.session.get('pdf_score', 0)
    total_questions = request.session.get('pdf_total_questions', 0)
    elements.append(Paragraph("Performance Summary", section_header_style))
    elements.append(Paragraph(f"Score: {score} out of {total_questions}", body_text_style))
    performance_percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    elements.append(Paragraph(f"Overall Performance: {performance_percentage:.2f}%", body_text_style))
    elements.append(Spacer(1, 0.2 * inch))


def add_topic_analysis(elements, request, section_header_style, body_text_style):
    incorrect_topics = request.session.get('pdf_incorrect_topics', [])
    
    # Append section header
    elements.append(Paragraph("Topic-wise Analysis", section_header_style))
    
    if incorrect_topics:
        # Generate formatted feedback
        feedback_md = generate_feedback(incorrect_topics)
        feedback_text = md_to_text(feedback_md)  # Convert Markdown to HTML
        
        # Use HTML paragraph formatting for better structure
        elements.append(Paragraph(feedback_text, body_text_style))
        elements.append(Spacer(1, 0.2 * inch))
    else:
        elements.append(Paragraph("All topics were answered correctly.", body_text_style))


def add_incorrect_questions_table(elements, request, section_header_style, body_text_style):
    incorrect_questions = request.session.get('incorrect_questions', [])
    if incorrect_questions:
        elements.append(Paragraph("Detailed Incorrect Questions", section_header_style))
        table_data = [["Topic", "Question", "Correct Answer"]]
        for question in incorrect_questions:
            table_data.append([question["topic"], question["question"], question["correct_answer"]])

        # Create and style the table
        table = Table(table_data, colWidths=[2 * inch, 3 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2 * inch))


def add_recommended_next_steps(elements, request, section_header_style, body_text_style):
    incorrect_topics = request.session.get('pdf_incorrect_topics', [])
    elements.append(Paragraph("Recommended Next Steps", section_header_style))
    if incorrect_topics:
        for topic in incorrect_topics:
            elements.append(Paragraph(f"- Focus on additional resources and practice questions for {topic}.", body_text_style))
        elements.append(Paragraph("Consider revisiting these topics with additional tutorials or practice tests.", body_text_style))
    else:
        elements.append(Paragraph("Excellent work! Continue to advance in other topics or explore new areas of study.", body_text_style))


def add_charts(elements, request):
    section_header_style = ParagraphStyle(name='SectionHeader', fontSize=14, leading=16, spaceAfter=8, textColor=colors.blue)
    score = request.session.get('pdf_score', 0)
    total_questions = request.session.get('pdf_total_questions', 0)
    incorrect_topics = request.session.get('pdf_incorrect_topics', [])

    # Score distribution chart
    elements.append(Paragraph("Score Distribution", section_header_style))
    score_dist_img = create_score_distribution_chart(score, total_questions)
    elements.append(Image(score_dist_img, width=5 * inch, height=3 * inch))
    elements.append(Spacer(1, 0.2 * inch))

    # Topic performance chart
    elements.append(Paragraph("Topic Performance", section_header_style))
    topic_perf_img = create_topic_performance_chart(total_questions, incorrect_topics)
    elements.append(Image(topic_perf_img, width=5 * inch, height=3 * inch))
    elements.append(Spacer(1, 0.2 * inch))

    # Incorrect topics frequency chart
    
    test_type = request.session.get('pdf_test_type')

    if test_type == 'generate_test':
        elements.append(Paragraph("Incorrect Topics Frequency", section_header_style))
        incorrect_topics_img = create_incorrect_topics_chart(request)
        elements.append(Image(incorrect_topics_img, width=5 * inch, height=3 * inch))
        elements.append(Spacer(1, 0.5 * inch))


def create_score_distribution_chart(score, total_questions):
    labels = ['Correct', 'Incorrect']
    values = [score, total_questions - score]
    colors = ['#4CAF50', '#FF6F61']
    
    fig, ax = plt.subplots()
    ax.bar(labels, values, color=colors)
    ax.set_title('Score Distribution')
    ax.set_ylabel('Count')

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='PNG')
    plt.close()
    img_buffer.seek(0)
    return img_buffer


def create_topic_performance_chart(total_questions, incorrect_topics):
    correct_topics = total_questions - len(incorrect_topics)
    incorrect_topics_count = len(incorrect_topics)
    sizes = [correct_topics, incorrect_topics_count]
    labels = ['Correct Topics', 'Incorrect Topics']
    colors = ['#8BC34A', '#FF5252']
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    ax.set_title('Topic Performance')

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='PNG')
    plt.close()
    img_buffer.seek(0)
    return img_buffer


def create_incorrect_topics_chart(incorrect_questions):
    topic_names = [q['topic'] for q in incorrect_questions]
    unique_topics, counts = np.unique(topic_names, return_counts=True)
    
    fig, ax = plt.subplots()
    ax.bar(unique_topics, counts, color='#FF7043')
    ax.set_title('Incorrect Topics Frequency')
    ax.set_xlabel('Topics')
    ax.set_ylabel('Mistakes Count')

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='PNG')
    plt.close()
    img_buffer.seek(0)
    return img_buffer