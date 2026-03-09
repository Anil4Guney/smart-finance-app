# Python'ın hafif ve hızlı bir sürümünü kullanıyoruz
FROM python:3.10-slim

# Konteyner içindeki çalışma dizinimiz
WORKDIR /app

# Çevresel değişkenler (Python'ın daha stabil çalışması için)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Bağımlılıkları kopyala ve kur
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Tüm kodları konteynere kopyala
COPY . /app/

# Django'nun çalışacağı portu aç
EXPOSE 8000

# Konteyner ayağa kalktığında çalışacak komut
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]