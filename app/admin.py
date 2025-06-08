from django.contrib import admin
from .models import Food_Entry, Exercise, WeightLog, Goal
import json

# Путь к файлу Exercises.json
EXERCISES_FILE_PATH = 'app/Exercises.json'

def load_group_choices():
    try:
        with open(EXERCISES_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
        groups = {}
        for exercise in data:
            group = exercise.get('group')
            group_code = exercise.get('group_code')
            if group and group_code and group not in groups:
                groups[group] = group_code
        return [(group, group) for group in groups.keys()], groups
    except Exception as e:
        print(f"Ошибка загрузки групп: {e}")
        return [], {}

GROUP_CHOICES, GROUP_CODES = load_group_choices()

class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'group_code')
    search_fields = ('name', 'group')
    list_filter = ('group',)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'group':
            kwargs['widget'] = admin.widgets.AdminRadioSelect(choices=GROUP_CHOICES)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Убедимся, что group_code обновляется корректно
        obj.group_code = GROUP_CODES.get(obj.group, 0)

        # Автоматическое заполнение ex_id, если оно не указано
        if not obj.ex_id:
            obj.ex_id = obj.group_code * 1000 + obj.id if obj.id else obj.group_code * 1000

        super().save_model(request, obj, form, change)

    fieldsets = (
        (None, {
            'fields': (
                ('name', 'group'),
                ('group_code', 'description'),
                'image_link',
            ),
            'description': 'Заполните основные данные об упражнении.'
        }),
    )

admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(WeightLog)
admin.site.register(Food_Entry)
admin.site.register(Goal)
