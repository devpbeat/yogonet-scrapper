# Use Python 3.8 as base image
FROM python:3.8

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 \
    libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 \
    fonts-liberation libnss3 lsb-release xdg-utils wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy all files to the working directory
COPY . .

# Create logs directory
RUN mkdir -p logs

# Set permissions on key file
RUN if [ -f /app/key.json ]; then chmod 400 /app/key.json; fi

# Set environment variable for application credentials
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/key.json"

# Print environment for debugging
RUN echo "GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS"
RUN if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then echo "Credentials file exists"; else echo "Credentials file does not exist"; fi

# Command to run the script
CMD ["python", "main.py"]