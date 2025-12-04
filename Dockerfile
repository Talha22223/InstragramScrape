# Use Python 3.11 slim image
FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r "freelance prj/backend/requirements.txt"

# Install frontend dependencies and build
WORKDIR "/app/freelance prj/frontend"
RUN npm install
RUN npm run build

# Go back to main directory
WORKDIR /app

# Expose port
EXPOSE 10000

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=10000

# Start the application
CMD ["python", "freelance prj/backend/app.py"]