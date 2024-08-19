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
ENV PATH="/venv/bin:$PATH" \
    OPENAI_API_KEY=sk-proj-T00QulUrYMuOBWPNz9J7T3BlbkFJE7oiXp19trN9iDusnEdD \
    LANGCHAIN_API_KEY=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 \
    LANGCHAIN_ENDPOINT=https://api.smith.langchain.com \
    LANGCHAIN_TRACING_V2=true


# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Selenium script and other necessary files
COPY . /app

# Expose the port your application will run on
EXPOSE 8000

# Start the application
ENTRYPOINT ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port 8000 --reload"]