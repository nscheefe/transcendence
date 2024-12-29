# Use a base image with Python 3.8 installed
FROM python:3.8-slim

# Install build dependencies and necessary libraries
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    git \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables to prevent .pyc files and buffer stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install virtualenv
RUN pip install virtualenv
