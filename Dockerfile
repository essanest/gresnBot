FROM python:3.13-slim

# نصب ابزارهای لازم برای کامپایل و کتابخانه‌های موردنیاز pandas
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    build-essential \
    libpython3-dev \
    libc6-dev \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# تنظیمات پروژه
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
