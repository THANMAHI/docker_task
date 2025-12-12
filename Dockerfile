# ---------- Stage 1: builder ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build deps and pip wheel cache target
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.11-slim

ENV TZ=UTC
ENV DATA_DIR=/data
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies (cron, tzdata)
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed python packages
COPY --from=builder /install /usr/local

# Copy app files
COPY . /app

# Ensure cron file has correct permissions and install it
RUN chmod 0644 /app/cron/2fa-cron && crontab /app/cron/2fa-cron

# Create persistent directories and set permissions
RUN mkdir -p /data /cron && chmod 0755 /data /cron

EXPOSE 8080

# Start cron and the API server
# Use sh -c to run both in foreground-ish manner: cron in background, uvicorn foreground
CMD service cron start && uvicorn app:app --host 0.0.0.0 --port 8080
