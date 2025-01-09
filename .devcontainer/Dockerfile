# Use a base image with Python 3.8 installed
FROM python:3.10

# Install build dependencies and necessary libraries
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    git \
    wget \
    protobuf-compiler \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*



# Set environment variables to prevent .pyc files and buffer stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install virtualenv
RUN pip install virtualenv

# Install go
# Set architecture variable first
ARG ARCH
RUN case $(uname -m) in \
        x86_64) echo "amd64" > /tmp/arch ;; \
        aarch64) echo "arm64" > /tmp/arch ;; \
        armv7l) echo "arm" > /tmp/arch ;; \
        i386) echo "386" > /tmp/arch ;; \
    esac && \
    export ARCH=$(cat /tmp/arch) && \
    wget "https://go.dev/dl/go1.23.3.linux-${ARCH}.tar.gz" && \
    tar -C /usr/local -xzf "go1.23.3.linux-${ARCH}.tar.gz" && \
    rm "go1.23.3.linux-${ARCH}.tar.gz"

# Add Go to PATH
ENV PATH=$PATH:/usr/local/go/bin
ENV GOPATH=/go
ENV PATH=$PATH:$GOPATH/bin

# Install protoc/grpc
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
RUN go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
