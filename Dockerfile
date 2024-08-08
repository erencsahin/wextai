# Temel imaj olarak resmi Python imajını kullan
FROM python:3.9-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinim dosyasını kopyala ve bağımlılıkları yükle
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını çalışma dizinine kopyala
COPY . /app/

# Django ayarlarını yap
ENV DJANGO_SETTINGS_MODULE=core.settings
ENV PYTHONUNBUFFERED=1

# Statik dosyaları topla (collectstatic)
RUN python manage.py collectstatic --noinput

# Sunucu başlatma komutu
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
