# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y upgrade && apt-get -y install wget

RUN mkdir -p ~/.postgresql && \
wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
    --output-document ~/.postgresql/root.crt && \
chmod 0600 ~/.postgresql/root.crt

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --default-timeout=100000000

COPY init_downloader.py init_downloader.py

# Preload model
RUN python3 init_downloader.py

# Copy the rest of the application code into the container
COPY . .

# Set the command to run your application
# This example assumes you have an `app.py` entry point; adjust as needed
CMD ["python3", "main.py"]