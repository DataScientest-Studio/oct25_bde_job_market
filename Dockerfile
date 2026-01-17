FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src

COPY models/ ./models

COPY .env .

EXPOSE 8000

CMD ["uvicorn", "src.api_main:api", "--host", "0.0.0.0", "--port", "8000"]
