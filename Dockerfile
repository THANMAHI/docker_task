###############################
# Stage 1: Builder
###############################
FROM python:3.11-slim AS builder

WORKDIR /app

# Install pip (python3 already included in python slim)
RUN apt-get update && \
    apt-get install -y python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .

# Install dependencies into /usr/local
RUN pip install -r requirements.txt


###############################
# Stage 2: Runtime
###############################
FROM python:3.11-slim

ENV TZ=UTC
WORKDIR /app

# Install cron + timezone
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set UTC timezone
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone

# Copy installed python packages & binaries from builder
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application package (your FastAPI code)
COPY app/ /app/

# Copy supporting scripts
COPY scripts/ /scripts/

# Copy RSA keys
COPY student_private.pem /app/student_private.pem
COPY student_public.pem /app/student_public.pem
COPY instructor_public.pem /app/instructor_public.pem

# Setup cron job (IMPORTANT: correct path)
RUN chmod 644 /app/cron/2fa-cron && crontab /app/cron/2fa-cron

# Create persistent volumes
RUN mkdir -p /data && mkdir -p /cron && chmod 755 /data /cron

VOLUME ["/data", "/cron"]

EXPOSE 8080

# Start cron + FastAPI server
CMD service cron start && uvicorn app.main:app --host 0.0.0.0 --port 8080
