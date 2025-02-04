ARG PYTHON_VERSION=3.9

# Builder
FROM python:${PYTHON_VERSION}-alpine AS builder

ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add --update git build-base libffi-dev curl-dev

WORKDIR /app

# Install requirements
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Install FFmpeg
ARG TARGETARCH
ARG FFMPEG_VERSION=4.2.2

RUN echo "Download from https://www.johnvansickle.com/ffmpeg/old-releases/ffmpeg-${FFMPEG_VERSION}-${TARGETARCH}-static.tar.xz" && \
    wget https://www.johnvansickle.com/ffmpeg/old-releases/ffmpeg-${FFMPEG_VERSION}-${TARGETARCH}-static.tar.xz -O ffmpeg.tar.xz && \
    tar Jxvf ./ffmpeg.tar.xz && \
    cp ./ffmpeg-${FFMPEG_VERSION}-${TARGETARCH}-static/ffmpeg /usr/local/bin/

# Runtime
FROM python:${PYTHON_VERSION}-alpine

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache curl

# Install FFmpeg
COPY --from=builder /usr/local/bin/ffmpeg /usr/local/bin/

# cURL Impersonate libraries
COPY --from=builder /usr/local/bin/curl_* /usr/local/bin/
COPY --from=builder /usr/local/lib/libcurl-* /usr/local/lib/

# Copy pip requirements
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY nazurin ./nazurin

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["python", "-m", "nazurin"]
