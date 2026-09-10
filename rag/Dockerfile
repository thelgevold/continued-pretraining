FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY rag/app /app/rag/app
COPY shared /app/shared
COPY rag/documents /app/rag/documents

CMD ["python", "-m", "rag.app.main"]
