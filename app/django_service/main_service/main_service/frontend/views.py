from django.shortcuts import render


def index(request):
    """
    View that handles the root URL `/` and renders the index.html template.
    """
    return render(request, 'frontend/index.html')
