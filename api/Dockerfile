FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY api/app /app/app
COPY shared /app/shared
COPY city_announcements /app/city_announcements

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
