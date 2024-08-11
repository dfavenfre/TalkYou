# Use the official Selenium Standalone Chrome image as the base
FROM selenium/standalone-chrome:latest

# Install Python and pip
USER root
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Create and activate a virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Selenium script and other necessary files
COPY . /app

# Adjust the container to work better with headless Chrome
# Disable the GPU and use a virtual framebuffer for headless Chrome
RUN apt-get update && \
    apt-get install -y xvfb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Expose the port your application will run on
EXPOSE 8000

# Start Xvfb and then run the application
CMD ["sh", "-c", "Xvfb :99 -screen 0 1280x1024x24 & export DISPLAY=:99 && uvicorn server:app --host 0.0.0.0 --port 8000 --reload"]
