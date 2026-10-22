FROM python:3.12-slim
WORKDIR /app
COPY services/service-carbone/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/service-carbone/ .
COPY shared/ ./shared/
EXPOSE 8002
CMD ["python", "main.py"]