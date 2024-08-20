FROM python:3.11-slim

RUN apt update

ENV REDIS_HOST=localhost \
    REDIS_PORT=6379dfaenfre

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../.. .
EXPOSE 8501

ENTRYPOINT ["streamlit","run"]

CMD ["talkyou.py"]