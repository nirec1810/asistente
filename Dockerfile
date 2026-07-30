FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY asistente/ asistente/
COPY frontend/ frontend/

EXPOSE ${PORT:-5000}

CMD ["python", "-m", "asistente.server"]
