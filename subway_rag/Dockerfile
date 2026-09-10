FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY subway_rag /app/subway_rag
COPY rag/documents/subway_network.txt /app/documents/subway_network.txt

CMD ["uvicorn", "subway_rag.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
