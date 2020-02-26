## -*- docker-image-name: "riji" -*- =======================
## 
## Dockerfile for the riji application
## 
## ---------------------------------------------------------
## Usage:
## 
## To build the container image 
## change into the directory of this Dockerfile
## and execute:
## 
##   docker build -t riji:latest .
## 
## Local Docker images can be listed with:
## 
##   docker images
## 
## The Docker container can be started with:
## 
##   docker run --name riji -d -p 8000:5000 --rm riji:latest
## 
## To debug it use:
## 
##   docker run --name riji -p 8000:5000 --rm riji:latest
## 
## To list the running containers use:
## 
##   docker ps
## 
## To stop the riji container use:
## 
##   docker stop riji
## 
## When the container is run locally riji can be accessed at:
## 
##   open http://localhost:8000/
## 
## ---------------------------------------------------------

# Start from Google's Cloud SDK Docker Alpine-based image
FROM google/cloud-sdk:alpine

# Make a new user to run riji
# This creates also the riji home directory /home/riji
RUN adduser -D riji

# Use /home/riji as working directory
WORKDIR /home/riji

# Update the index of available packages
RUN apk update

# Install development tools 
# needed to install google-cloud-translate package
RUN apk add --no-cache build-base linux-headers

# Install python3
RUN apk add --no-cache python3 python3-dev

# Install a virtual Python environment
RUN python3 -m venv venv

# Update pip
RUN venv/bin/pip install --upgrade pip

# Install requirements for riji
COPY requirements.txt requirements.txt
RUN venv/bin/pip install -r requirements.txt

# Install gunicorn as web server
RUN venv/bin/pip install gunicorn pymysql

# Install riji sources
COPY app app
COPY migrations migrations
COPY riji.py config.py boot.sh ./
RUN chmod a+x boot.sh
RUN chown -R riji:riji ./

# Install environment
COPY .env/production .env
RUN chown -R riji:riji .env
RUN chmod 400 .env/*
RUN chmod 500 .env

# The flask command relies on the FLASK_APP environment variable to
# know how to start the application
ENV FLASK_APP riji.py

# Switch to riji user
USER riji

# Indicate the port on which the container should listen for connections
# The standard Flask port is 5000
EXPOSE 5000

# Start riji via boot.sh
ENTRYPOINT ["./boot.sh"]

## =========================================================
## =========================================================

## fin.
