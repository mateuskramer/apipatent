FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-80} --proxy-headers"
