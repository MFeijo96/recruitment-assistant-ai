FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AAMAD_TARGET_RUNTIME=crewai \
    CREWAI_TELEMETRY_OPTOUT=true

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/

RUN python -m pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 appuser

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)" || exit 1

CMD ["python", "-m", "uvicorn", "recruitment_assistant.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]