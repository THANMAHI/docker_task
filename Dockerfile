###############################
# Stage 1: Builder
###############################
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies to default python location
RUN pip install -r requirements.txt


###############################
# Stage 2: Runtime
###############################
FROM python:3.11-slim

ENV TZ=UTC
WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3 python3-pip cron tzdata procps && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set timezone
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone

# Copy Python packages & binaries
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY app.py .
COPY decrypt_seed.py .
COPY totp_utils.py .
COPY student_private.pem .
COPY student_public.pem .
COPY instructor_public.pem .

COPY scripts/ ./scripts/
COPY cron/ ./cron/

# Install cron job
RUN chmod 644 /app/cron/2fa-cron && crontab /app/cron/2fa-cron

# Create persistent volumes
RUN mkdir -p /data && mkdir -p /cron && chmod 755 /data /cron

VOLUME ["/data", "/cron"]

EXPOSE 8080

CMD service cron start && uvicorn app:app --host 0.0.0.0 --port 8080
