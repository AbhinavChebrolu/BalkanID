# Use the official Python image as the base image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the required packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the source code to the working directory
COPY . .

# Expose port 8000 for the web server
EXPOSE 8000

# Start the application
CMD ["python3", "app.py"]


'''
In this Dockerfile, we start with the official Python 3.9 slim-buster image as the base image. We then set the working directory to /app, copy the requirements.txt file, install the required packages, and copy the source code to the working directory.
We expose port 8000 for the web server, which is the port used by the Flask app in our code. Finally, we set the command to start the application using CMD ["python3", "app.py"].
To build the Docker image, we can run the following command in the directory where the Dockerfile and the app.py file are located
'''

docker build -t my-app .

#  This will build the Docker image and tag it with the name my-app.
#  To run the Docker container, we can use the following command:

docker run -p 8000:8000 my-app

#  This will start the container and map port 8000 from the container to port 8000 on the host machine.
#  Once the container is running, we can access the endpoint to download the CSV file by visiting http://localhost:8000/download. The CSV file will be downloaded to the local machine.
