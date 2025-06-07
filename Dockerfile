FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

# Установка зависимостей системы 
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Переменные окружения для Django
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=ActivityWatch.settings

EXPOSE 8000

CMD ["gunicorn", "ActivityWatch.wsgi:application", "--bind", "0.0.0.0:8000"]
