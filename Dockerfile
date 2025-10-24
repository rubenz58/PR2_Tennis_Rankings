# Stage 1: Build the React frontend
FROM node:18 AS frontend-build
WORKDIR /app/frontend
# Copy frontend package files
COPY frontend/package*.json ./
# Install frontend dependencies
RUN npm install
# Copy all frontend source code
COPY frontend/ ./
# Set API URL for production (same domain since backend serves frontend)
ENV REACT_APP_API_URL=""
# Build the React app (creates build/ folder)
RUN npm run build

# Stage 2: Build the Python backend
# Use Python 3.9 as base image
FROM python:3.9-slim
# Set working directory inside container
WORKDIR /app
# Install system dependencies for Chrome/Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || true \
    && apt-get update \
    && apt-get install -f -y \
    && rm google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*
# Don't install ChromeDriver manually - let webdriver-manager handle it
# (Your Python code already uses ChromeDriverManager().install())
# Copy Python requirements
COPY backend/Pipfile backend/Pipfile.lock ./

# Install pipenv and Python dependencies
RUN pip install pipenv && \
    pipenv install --system --deploy
# Copy the backend application (excluding build folder for now)
COPY backend/ .
# Copy the built frontend from the frontend-build stage
COPY --from=frontend-build /app/frontend/build ./build
# Create logs directory
RUN mkdir -p logs
# Expose port 8080 for Railway
EXPOSE 8080
# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
# Command to run the application
CMD ["python", "app.py"]