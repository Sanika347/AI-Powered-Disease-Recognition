# Use an official Python image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Render uses $PORT)
EXPOSE 10000

# Run Streamlit
CMD ["streamlit", "run", "home.py", "--server.port", "10000", "--server.address", "0.0.0.0"]
