ARG PYTHON_VERSION=3.8

ARG CURL_IMPERSONATE_VERSION=0.5-chrome
FROM lwthiker/curl-impersonate:${CURL_IMPERSONATE_VERSION} AS curl

# Builder
FROM python:${PYTHON_VERSION}-alpine AS builder

RUN apk add --update git build-base libffi-dev curl-dev

WORKDIR /root

COPY --from=curl /usr/local/bin/curl_* /usr/local/bin/
COPY --from=curl /usr/local/lib/ /usr/local/lib/

# Install requirements
COPY requirements.txt /root
RUN pip install --prefix="/install" --no-warn-script-location -r requirements.txt

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
COPY --from=builder /install /usr/local

# Copy CA certificates for curl_cffi, can be removed once v0.6 is officially released
RUN PYTHON_LIB_PATH="$(python -c 'import site; print(site.getsitepackages()[0])')" &&\
    CA_FILE="$(python -c 'import certifi; print(certifi.where())')" && \
    cp "$CA_FILE" "$PYTHON_LIB_PATH"/curl_cffi/

WORKDIR /app
COPY nazurin ./nazurin

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["python", "-m", "nazurin"]
