# Voice line (voice/ + deskagent) for Railway or any Docker host. Build from the repo root:
#   docker build -f deploy/Dockerfile .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY deskagent/ deskagent/
COPY voice/ voice/
COPY triage/ triage/
COPY scorer/ scorer/
COPY scripts/ scripts/

# The organisers' public cases, for the caller's shipment lookup. Fetched at build time, never committed.
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && bash scripts/fetch_cases.sh /app/data/public-cases \
    && rm -rf /app/data/public-cases/.git \
    && apt-get purge -y git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Everything the app writes goes under /data, so one Railway volume keeps it across deploys.
ENV VOICE_CASES_DIR=/data/voice/cases \
    VOICE_LOG_DIR=/data/voice \
    OUTBOX_SENT_DIR=/data/sent \
    VOICE_SHIPMENT_DATA="/app/data/public-cases/Delivery & Logistics"

RUN useradd --create-home --uid 1000 app && mkdir -p /data && chown app:app /data
USER app

EXPOSE 8010
CMD ["sh", "-c", "exec uvicorn voice.app:app --host 0.0.0.0 --port ${PORT:-8010}"]
