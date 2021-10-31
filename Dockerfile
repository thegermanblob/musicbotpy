# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
RUN apt-get update && apt-get install ffmpeg -y
COPY . .
CMD ["python3", "-m", "Bot"]