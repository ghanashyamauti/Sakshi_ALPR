# ==============================================================================
# Sakshi ALPR India - Frontend Production Dockerfile
# Optimized for Render, Railway, Fly.io, and Docker Compose
# ==============================================================================

FROM python:3.11-alpine

# Set environment flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=3000 \
    BACKEND_URL=http://localhost:8000

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend source
COPY . .

# Expose web dashboard port
EXPOSE 3000

# Start lightweight frontend server with dynamic backend URL injection
CMD ["python", "run_frontend.py"]

