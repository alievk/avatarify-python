# Use the official Ubuntu image as the base image
FROM ubuntu:20.04

# Set the working directory inside the container
WORKDIR /app

# Update the package list and install necessary dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy the local contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the port on which the app will run
EXPOSE 8080

# Specify the command to run your application
CMD ["python3", "app.py"]
