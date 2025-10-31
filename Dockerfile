# Dockerfile - tuned for Streamlit + Tesseract + Poppler
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install tesseract, poppler and OS deps for Pillow/OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libtesseract-dev \
    libleptonica-dev \
    libjpeg-dev \
    zlib1g-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python deps first for caching
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app

# Make the start script executable
RUN chmod +x /app/start.sh

EXPOSE 8501

# Entrypoint
CMD ["/app/start.sh"]
