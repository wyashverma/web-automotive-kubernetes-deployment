FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for PDF generation
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpango1.0-dev \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create reports directory
RUN mkdir -p /app/reports

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
