FROM python:3.14-slim

# Set the working directory
WORKDIR /app

# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output is sent directly to terminal (no buffering)
ENV PYTHONUNBUFFERED=1

# Install dependencies
# We copy this first to leverage Docker layer caching for pip install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 8000

# Start the application with Gunicorn, running migrations first
CMD ["sh", "-c", "alembic upgrade head && gunicorn src:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000"]
