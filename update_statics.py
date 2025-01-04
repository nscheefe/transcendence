import os
import re

# Define the directory containing your HTML files
directory = '/Users/max/Projekte/transcendence/app/django_service/main_service/main_service/frontend/templates/frontend/'

# Define the regex patterns for CSS, JS, and image files
patterns = {
    'css': re.compile(r'(<link.*?href=")(css/.*?\.css)(".*?>)'),
    'js': re.compile(r'(<script.*?src=")(js/.*?\.js)(".*?>)'),
    'images': re.compile(r'(<img.*?src=")(images/.*?\.)(jpg|jpeg|png|gif|ico)(".*?>)')
}

# Function to update the file content
def update_file_content(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Add {% load static %} if not present
    if '{% load static %}' not in content:
        content = content.replace('<head>', '<head>\n  {% load static %}')

    # Replace static file paths with {% static %} template tag
    for key, pattern in patterns.items():
        content = pattern.sub(r'\1{% static "\2\3" %}\3', content)

    with open(file_path, 'w') as file:
        file.write(content)

# Iterate over all HTML files in the directory
for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            file_path = os.path.join(root, file)
            update_file_content(file_path)

print("Static file paths updated successfully.")
