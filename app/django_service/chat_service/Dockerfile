# Use a base image with Python 3.8 installed (adjust as needed)
FROM python:3.8-slim

# Install build dependencies and necessary libraries
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables to prevent .pyc files and buffer stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create and set the working directory
WORKDIR /usr/src/app

# Copy requirements.txt into the working directory
COPY requirements.txt /usr/src/app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure grpcio-tools is installed
RUN pip install grpcio-tools

# Copy the rest of the application code
COPY . /usr/src/app/

# Ensure the protos directory exists in the desired location
RUN mkdir -p chat_service/protos

# Generate gRPC files from proto files
RUN python -m grpc_tools.protoc -I./protos --python_out=./chat_service/protos --grpc_python_out=./chat_service/protos ./protos/*.proto
RUN /bin/sh -c python manage.py migrate
# Expose the port for the gRPC server
EXPOSE 50051

# Command to run the gRPC server
CMD ["python", "manage.py", "grpcrunserver", "--dev"]