# test/utils.py
import google.generativeai as genai
import random
import json
import re
from urllib.parse import urlparse
from markdown import markdown
from bs4 import BeautifulSoup
import markdown


# Configure API Key
genai.configure(api_key="Your API Key")

def generate_mcq_question(topic):
    """
    Generates a multiple-choice question using an AI model based on a given topic.

    Parameters:
    - topic (str): The topic for which to generate a question.

    Returns:
    - dict: A dictionary containing the question, options, and correct answer.
    """
    # Structured prompt for consistent formatting
    ask = (
        f"Generate a multiple-choice question on the topic '{topic}'. "
        "Format answer as:\n\n"
        "Question: [Your question]\n"
        "A) Option 1\n"
        "B) Option 2\n"
        "C) Option 3\n"
        "D) Option 4\n\n"
        "Correct Answer: [Letter of correct option]"
    )

    # Call the AI model to generate the question
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(ask)
        response_text = response.text
    except Exception as e:
        print(f"Error generating question: {e}")
        return None

    # Parse the AI response for structured data extraction
    def parse_response(response_text):
        lines = response_text.strip().split('\n')

        # Extract the question
        question_line = next((line for line in lines if line.startswith("Question:")), None)
        question = question_line.split(":", 1)[1].strip() if question_line else None

        # Extract options
        options = {}
        for line in lines:
            if line.startswith(("A)", "B)", "C)", "D)")):
                key, value = line.split(")", 1)
                options[key.strip()] = value.strip()

        # Extract correct answer
        correct_answer_line = next((line for line in lines if line.startswith("Correct Answer:")), None)
        correct_answer = correct_answer_line.split(":", 1)[1].strip() if correct_answer_line else None

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer
        }

    # Parse and return structured data
    parsed_data = parse_response(response_text)
    return parsed_data


def is_valid_url(url):
    """Check if the URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def Ai_course_recom(incorrect_topics):
    python = [
        'https://www.udemy.com/course/data-engineering-101-the-beginners-guide/',
        'https://www.udemy.com/course/the-complete-sql-bootcamp/',
        'https://www.udemy.com/course/data-warehouse-the-ultimate-guide/',
        'https://www.udemy.com/course/etl-developer-mysql-data-migration-ms-sql-server-ssis/',
        'https://www.udemy.com/course/hands-on-hadoop-masterclass-tame-the-big-data/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/learn-data-lake-fundamentals/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/apache-spark-programming-in-python-for-beginners/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/the-complete-hands-on-course-to-master-apache-airflow/',
        'https://www.udemy.com/course/aws-data-engineer/'
    ]
    net = [
        'https://www.udemy.com/course/asp-net-core-true-ultimate-guide-real-project/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/complete-aspnet-core-21-course/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/build-rest-apis-with-aspnet-core-web-api-entity-framework/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/csharp-oops-mvc-asp-dotnet-core-webapi-sql-questions-mock-interviews/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/aspnet-mvc-course-aspnet-core/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/complete-aspnet-core-31-and-entity-framework-development/?couponCode=KEEPLEARNING'
    ]
    java = [
        'https://www.udemy.com/course/java-the-complete-java-developer-course/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/java-se-programming/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/java-programming-tutorial-for-beginners/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/the-complete-java-development-bootcamp/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/full-stack-java-developer-java/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/java-programming-a-comprehensive-bootcamp-from-zero-to-hero/?couponCode=KEEPLEARNING',
        'https://www.udemy.com/course/spring-5-with-spring-boot-2/?couponCode=KEEPLEARNING'
    ]

   # Embed the predefined arrays directly into the prompt for better AI guidance
    prompt = (
        f"I have identified the following topics I am weak in: {', '.join(incorrect_topics)}. "
        "Here are the available course links: "
        f"Python courses: {', '.join(python)}; "
        f".NET courses: {', '.join(net)}; "
        f"Java courses: {', '.join(java)}. "
        "Based on these, please select and recommend the most relevant courses according to the weak topics mentioned. "
        "Return the result in JSON format with these fields: course_name, course_link, platform, and course_image_link. "
        "Ensure course_image_link is a valid URL."
    )

    # The rest of the function
    while incorrect_topics:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Use regex to extract JSON from the response text
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)  # Get the matched JSON string
            try:
                courses = json.loads(json_str)
                
                # Validate the image links
                for course in courses:
                    image_link = course.get("course_image_link")
                    if not is_valid_url(image_link):
                        # Set a standard image link if the provided link is invalid
                        course["course_image_link"] = "https://example.com/standard-image.jpg"  # Replace with your default image URL

                return courses

            except json.JSONDecodeError:
                print("Failed to decode JSON response. Response text:", response_text)
                return []
            except Exception as e:
                print(f"An error occurred: {e}")
                return []
    
    return []



# List of available course image links
image_links = [
    "https://img-c.udemycdn.com/course/480x270/567828_67d0.jpg",
    "https://img-c.udemycdn.com/course/480x270/2776760_f176_10.jpg",
    "https://img-b.udemycdn.com/course/480x270/903744_8eb2.jpg",
    "https://img-c.udemycdn.com/course/480x270/543600_64d1_4.jpg",
    "https://img-c.udemycdn.com/course/480x270/629302_8a2d_2.jpg",
    "https://img-c.udemycdn.com/course/480x270/692188_9da7_34.jpg",
    "https://img-c.udemycdn.com/course/480x270/2473048_8255_5.jpg",
    "https://img-c.udemycdn.com/course/480x270/903378_f32d_7.jpg",
    "https://img-c.udemycdn.com/course/480x270/822444_a6db.jpg",
    "https://img-c.udemycdn.com/course/480x270/836376_8b97_4.jpg",
    "https://img-c.udemycdn.com/course/480x270/1350984_2355_6.jpg",
    "https://img-c.udemycdn.com/course/480x270/1340588_e1b6_4.jpg",
    "https://img-c.udemycdn.com/course/480x270/1386294_cf10_3.jpg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~SPECIALIZATION!~ibm-full-stack-cloud-developer/XDP~SPECIALIZATION!~ibm-full-stack-cloud-developer.jpeg",
    "https://img-c.udemycdn.com/course/480x270/1565838_e54e_18.jpg",
    "https://img-c.udemycdn.com/course/480x270/1646980_23f7_3.jpg",
    "https://img-b.udemycdn.com/course/480x270/2306676_57ba_2.jpg",
    "https://via.placeholder.com/300x200",
    "https://img-c.udemycdn.com/course/480x270/1672410_9ff1_5.jpg",
    "https://img-c.udemycdn.com/course/480x270/3716888_5054.jpg",
    "https://img-b.udemycdn.com/course/480x270/959700_8bd2_12.jpg",
    "https://img-c.udemycdn.com/course/480x270/382002_5d4a_3.jpg",
    "https://s.udemycdn.com/meta/default-meta-image-v2.png",
    "https://img-c.udemycdn.com/course/480x270/806922_6310_3.jpg",
    "https://s.udemycdn.com/meta/default-meta-image-v2.png",
    "https://img-b.udemycdn.com/course/480x270/383576_fd27_4.jpg",
    "https://img-c.udemycdn.com/course/480x270/356030_0209_6.jpg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~SPECIALIZATION!~java-programming/XDP~SPECIALIZATION!~java-programming.jpeg",
    "https://img-c.udemycdn.com/course/480x270/533682_c10c_4.jpg",
    "https://img-c.udemycdn.com/course/480x270/1535678_0ce9_7.jpg",
    "https://img-c.udemycdn.com/course/480x270/358540_d06b_16.jpg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~SPECIALIZATION!~java-programming/XDP~SPECIALIZATION!~java-programming.jpeg",
    "https://img-c.udemycdn.com/course/480x270/533682_c10c_4.jpg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~COURSE!~object-oriented-java/XDP~COURSE!~object-oriented-java.jpeg",
    "https://img-c.udemycdn.com/course/480x270/1656228_5278_5.jpg",
    "https://img-c.udemycdn.com/course/480x270/1217894_e8cc_4.jpg",
    "https://img-c.udemycdn.com/course/480x270/1419186_5b21_2.jpg",
    "https://img-c.udemycdn.com/course/480x270/1352468_3d97_8.jpg",
    "https://img-c.udemycdn.com/course/480x270/2208130_c37b_6.jpg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~SPECIALIZATION!~ibm-data-science/XDP~SPECIALIZATION!~ibm-data-science.jpeg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~SPECIALIZATION!~jhu-data-science/XDP~SPECIALIZATION!~jhu-data-science.jpeg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~COURSE!~machine-learning/XDP~COURSE!~machine-learning.jpeg",
    "https://img-c.udemycdn.com/course/480x270/821726_8071.jpg",
    "https://img-b.udemycdn.com/course/480x270/903744_8eb2.jpg",
    "https://img-c.udemycdn.com/course/480x270/513244_b831_4.jpg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~SPECIALIZATION!~deep-learning/XDP~SPECIALIZATION!~deep-learning.jpeg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~COURSE!~r-programming/XDP~COURSE!~r-programming.jpeg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~COURSE!~data-analysis-with-python/XDP~COURSE!~data-analysis-with-python.jpeg",
    "https://img-c.udemycdn.com/course/480x270/1298780_731f_4.jpg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~SPECIALIZATION!~data-science-python/XDP~SPECIALIZATION!~data-science-python.jpeg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~COURSE!~sql-for-data-science/XDP~COURSE!~sql-for-data-science.jpeg",
    "https://s3.amazonaws.com/coursera_assets/meta_images/generated/XDP/XDP~COURSE!~machine-learning-with-python/XDP~COURSE!~machine-learning-with-python.jpeg",
    "https://www.cdmi.in/courses@2x/python-training-institute.webp",
    "https://www.clariwell.in/resources/best-java-certification-course-top-training-institute-in-pune.webp",
]


def get_unique_image_links(num_links):
    # Shuffle the image links randomly
    random.shuffle(image_links)
    
    # Select the first num_links from the shuffled list
    unique_links = image_links[:num_links]
    return unique_links


def generate_feedback(incorrect_topics):
    # Create a structured prompt based on the number of topics
    if len(incorrect_topics) > 2:
        prompt_parts = []
        for topic in incorrect_topics:
            prompt_parts.append(f"Provide constructive feedback for the topic: {topic}. Suggest study techniques, useful resources, and practical exercises to deepen understanding.")
        prompt = " ".join(prompt_parts)
    else:
        topic_list = ', '.join(incorrect_topics)  # Join topics in a readable format
        prompt = (
            f"The student is experiencing challenges in these topics: {topic_list}. "
            "Provide constructive feedback to help them improve. "
            "Include a couple of paragraphs suggesting study techniques, useful resources, and practical exercises "
            "to deepen their understanding."
        )

    # Generate content using the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # Convert response to structured Markdown for easier HTML processing later
    response_md = f"## Feedback on Improvement\n\n{response.text}"
    return response.text


def md_to_html(md):
    # Convert Markdown to HTML
    html_content = markdown(md)
    
    # Parse HTML for additional styling or formatting with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Optional: Add custom styling
    for heading in soup.find_all(['h1', 'h2', 'h3']):
        heading['class'] = 'pdf-heading'
    for paragraph in soup.find_all('p'):
        paragraph['class'] = 'pdf-paragraph'
    
    return soup.prettify()  # Convert to a formatted HTML string


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