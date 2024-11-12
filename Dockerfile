# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt first to install dependencies
COPY requirements.txt /app/

# Install system dependencies (you may need to install additional packages for your app)
RUN apt-get update && apt-get install -y \
    gcc
# Install Python dependencies from requirements.txt
RUN pip install -r /app/requirements.txt

# Now copy the rest of your application code
COPY . /app

# Expose the port the app will run on
EXPOSE 8080

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "src.fastapi_app:app", "--host", "0.0.0.0", "--port", "8080"]
