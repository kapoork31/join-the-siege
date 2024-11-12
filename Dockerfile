# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy everything from the current directory (root folder) into the container's /app directory
COPY . /app

# Install system dependencies (you may need to install additional packages for your app)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the port the app will run on
EXPOSE 8080

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "src.fastapi_app:app", "--host", "0.0.0.0", "--port", "8080"]
