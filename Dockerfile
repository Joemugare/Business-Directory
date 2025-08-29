# Useofficial Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set Django settings module
ENV DJANGO_SETTINGS_MODULE=business_directory.settings

# Set a temporary secret key for collectstatic during build
# In production, pass this via docker-compose or build args
ENV DJANGO_SECRET_KEY=temporary-build-secret-key-for-collectstatic

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
ENV PORT=8000
EXPOSE $PORT

# Run Gunicorn
CMD ["sh", "-c", "gunicorn business_directory.wsgi:application --bind 0.0.0.0:$PORT --workers 1"]