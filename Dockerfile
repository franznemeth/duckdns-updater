# ── base image ────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

WORKDIR /app

# Create a non-root user early so we own the workdir
RUN adduser --disabled-password --gecos "" appuser

# ── dependencies ──────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── application ───────────────────────────────────────────────────────────────
COPY updater.py .

# Drop to non-root
USER appuser

ENTRYPOINT ["python", "updater.py"]

