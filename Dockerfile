FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Cairo/Africa

RUN apt-get update && \
    apt-get install -y nano

WORKDIR /app

# Copy requirements file to the working directory
COPY requirements.txt .

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies using wheels (fall back to source if necessary)
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt --no-warn-script-location

# Copy the application code into the image
COPY . /app/

# Create a non-root user
RUN useradd -m appuser

# Change ownership of the application directory
RUN chown -R appuser /app

# Switch to the new user
USER appuser