FROM python:3.13-slim

# نصب ابزارهای لازم برای کامپایل
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# تنظیمات پروژه
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
