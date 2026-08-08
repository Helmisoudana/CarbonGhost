FROM python:3.12-slim
WORKDIR /app
COPY services/service-mesures/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/service-mesures/ .
COPY shared/ ./shared/
EXPOSE 8003
CMD ["python", "main.py"]