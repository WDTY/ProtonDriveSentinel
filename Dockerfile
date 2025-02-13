FROM python:3.9-slim

# Install necessary packages including Chrome and ChromeDriver
RUN apt-get update && apt-get install -y     chromium chromium-driver     && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script and configuration file
COPY monitor.py .
COPY config.ini .

# Set the command to execute the script
CMD ["python", "monitor.py"]
