FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 LEARNING_HOST=0.0.0.0 LEARNING_PORT=8791 LEARNING_DB=/state/learning.sqlite3 LEARNING_CONTENT_IMPORT=0
WORKDIR /app
COPY app ./app
COPY content ./content
COPY solutions ./solutions
COPY scripts/build_content.py scripts/add_daily_plan.py scripts/backup_progress.py scripts/export_reference_batch.py scripts/import_batch.py ./scripts/
COPY server.py storage.py ./
RUN python scripts/build_content.py && mkdir /state && chown 10001:10001 /state
USER 10001:10001
EXPOSE 8791
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import http.client; c=http.client.HTTPConnection('127.0.0.1',8791,timeout=2); c.request('GET','/api/progress'); r=c.getresponse(); r.read(); raise SystemExit(0 if r.status==200 else 1)"
CMD ["python", "server.py"]
