# Use the official Python image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY . /app/

# Expose the port that the application will run on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]