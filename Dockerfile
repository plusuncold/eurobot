# Use Ubuntu 24.04 as the base image
FROM ubuntu:24.04

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install Python, pip, and other necessary dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Create a virtual environment and activate it
RUN python3 -m venv /app/venv

# Ensure pip is up-to-date in the virtual environment
RUN /app/venv/bin/pip install --upgrade pip

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies in the virtual environment
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .
