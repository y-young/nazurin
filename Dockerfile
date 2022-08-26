ARG PYTHON_VERSION=3.8

# Builder
FROM python:${PYTHON_VERSION}-slim as builder

WORKDIR /root
COPY requirements.txt /root

# Install requirements
RUN apt update && apt install -y python3-pip git
RUN pip install --prefix="/install" --no-warn-script-location -r requirements.txt

# Runtime
FROM python:${PYTHON_VERSION}-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Copy pip requirements
COPY --from=builder /install /usr/local

# Install FFmpeg
RUN apt-get update && \
    apt-get install --no-install-recommends -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY nazurin ./nazurin

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["python", "-m", "nazurin"]
