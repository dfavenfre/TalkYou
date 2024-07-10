FROM python:3.11-slim-bookworm

RUN apt update

ENV REDIS_HOST=localhost \
    REDIS_PORT=6379dfaenfre

WORKDIR /app

COPY . /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt
COPY .. .
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000" ,"--reload"]