ARG PYTHON_VERSION=3.8

FROM jrottenberg/ffmpeg:4.2-scratch as ffmpeg

# Builder
FROM python:${PYTHON_VERSION}-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends git

WORKDIR /root

# Install requirements
COPY requirements.txt /root
RUN pip install --prefix="/install" --no-warn-script-location -r requirements.txt

# Runtime
FROM python:${PYTHON_VERSION}-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install FFmpeg
COPY --from=ffmpeg / /

# Copy pip requirements
COPY --from=builder /install /usr/local

WORKDIR /app
COPY nazurin ./nazurin

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["python", "-m", "nazurin"]
