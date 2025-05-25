# Run this file with:
# python manage.py shell < jsonToDatabase.py

import os
import django

# Настройка Django, если скрипт запущен напрямую
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'FitTrack.settings'
    django.setup()

# Add Exercises from json file to database
import json
from app.models import Exercise
with open('app/Exercises.json', encoding='utf-8') as f:
    exer_json = json.load(f)

for exe in exer_json:
    try:
        obj, created = Exercise.objects.get_or_create(
            name=exe['name'],
            defaults={
                'group': exe['group'],
                'group_code': exe['group_code'],
                'description': exe['description'],
                'image_link': exe['image_link'],
                'ex_id': exe['ex_id'],
            }
        )
        if created:
            print(f"Добавлено: {exe['name']}")
        else:
            print(f"Пропущено (уже есть): {exe['name']}")
    except Exception as e:
        print(f"Ошибка при добавлении {exe['name']}: {e}")
