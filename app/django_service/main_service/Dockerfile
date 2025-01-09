# Dockerfile for main_service

FROM python:3.10-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Ensure grpcio-tools is installed
RUN pip install grpcio-tools

# Copy the entire application directory to the container
COPY . .

# Ensure the protos directory exists in the desired location
RUN mkdir -p main_service/protos

# Compile proto files and place the output in the main_service/protos directory
RUN python -m grpc_tools.protoc -I./protos --python_out=./main_service/protos --grpc_python_out=./main_service/protos ./protos/*.proto

# Expose port and set the entrypoint
EXPOSE 8000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "main_service.asgi:application"]
