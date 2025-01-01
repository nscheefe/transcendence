# Step 1: Use an official image that includes a C++ compiler
FROM ubuntu:20.04

# Set environment variable to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Step 2: Install dependencies (build-essential includes gcc/g++ compilers and git)
RUN apt-get update && apt-get install -y \
    tzdata \
    build-essential \
    cmake \
    git \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Configure tzdata package
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Step 3: Set the working directory in the container
WORKDIR /app

# Step 4: Clone your GitHub repository
RUN git clone https://github.com/RowMax03/webserv.git .

# Step 5: Compile the C++ web server (assuming Makefile or CMakeLists.txt exists)
RUN make

# Alternatively, for CMake, uncomment these:
# RUN cmake .
# RUN make

# Step 6: Expose the port your web server will run on (e.g., 8080)
EXPOSE 8080

# Step 7: Define the command to run your web server
CMD ["./webserv", "tester.conf"]
