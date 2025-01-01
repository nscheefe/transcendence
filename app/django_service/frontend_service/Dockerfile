# Dockerfile for frontend_service

FROM python:3.11

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application directory to the container
COPY . .

# Expose port and set the entrypoint
EXPOSE 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "frontend_service.wsgi:application"]
