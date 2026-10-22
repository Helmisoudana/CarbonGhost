FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY services/service-assistant/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/service-assistant/ .
COPY shared/ ./shared/

EXPOSE 8005

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
