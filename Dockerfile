# Dockerfile

# 1. Base Image: Use a slim, official Python image
FROM python:3.10-slim

# Set environment variables to prevent interactive prompts during installation
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 2. System Dependencies: Install Chrome and other tools in a single layer
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    # Install Google Chrome
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    # Clean up to reduce image size
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# 3. Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app

# 4. Install Python Dependencies (Leveraging Docker Caching)
# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Code
# Chown is needed to give the new user ownership of the files
COPY --chown=appuser:appuser . .

# 6. Switch to the non-root user
USER appuser

# 7. Expose Port and Run Application with Gunicorn (Production Server)
EXPOSE 8000
# -w 4: Spawns 4 worker processes. Adjust based on your Render plan's CPU/RAM.
# -k uvicorn.workers.UvicornWorker: Use Uvicorn to run the ASGI app (FastAPI).
# -b 0.0.0.0:8000: Bind to all network interfaces on port 8000.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app"]