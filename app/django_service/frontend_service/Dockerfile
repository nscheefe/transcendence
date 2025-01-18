# Dockerfile for frontend_service

FROM python:3.10-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application directory to the container
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port and set the entrypoint
EXPOSE 80
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
