# Use NVIDIA CUDA base image
FROM nvidia/cuda:11.8.0-base-ubuntu22.04

# Install Python, pip, and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    ffmpeg \
    wget \
    curl \
    gnupg \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome and ChromeDriver
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install specific version of ChromeDriver
RUN CHROMEDRIVER_VERSION=114.0.5735.90 \
    && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# Set the working directory
WORKDIR /app

# Create and activate a virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH" \
    OPENAI_API_KEY=<ADD-YOUR-OWN-OPENAI-API-KEY> \
    LANGCHAIN_API_KEY=<ADD-YOUR-OWN-LANGSMITH-API-KEY> \
    LANGCHAIN_ENDPOINT=https://api.smith.langchain.com \
    LANGCHAIN_TRACING_V2=true

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install git+https://github.com/openai/whisper.git \
    && pip install --no-cache-dir -r requirements.txt


# Copy the application files
COPY . /app

# Expose the port your application will run on
EXPOSE 8000

# Start the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


