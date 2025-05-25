from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from datetime import date, datetime, timedelta
from django.contrib.auth import logout
from django.utils import timezone
from .models import Food_Entry
from exlog_app.models import ExerciseLog, Exercise as Exercise_App
from .forms import FoodForm
from django.db.models import Avg, Count
from .forms import FoodFormTheSecond
from .models import Exercise
from .models import WeightLog
from .forms import WeightLogForm
from . import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import csv
from django.templatetags.static import static
from django.db import models
import json

def button_class(active_exercise, button):
    if active_exercise == button:
        return 'btn btn-outline-secondary btn-sm active'
    else:
        return 'btn btn-outline-secondary btn-sm'


# Create your views here.
def home(request):
    context = {
        'title': 'Home'
    }
    return render(request, 'app/home.html', context)


def exercises(request, active_exercises=0):
    """
    Отображает список упражнений и соответствующую диаграмму тела.
    """
    if not request.user.is_authenticated:
        return redirect('app:login')

    button_codes = [102, 106, 103, 110, 111, 112, 113, 114, 117, 118, 120, 121, 119, 101, 104]
    classes = {f'button{i+1}_class': button_class(active_exercises, code) for i, code in enumerate(button_codes)}

    # Путь к диаграмме тела
    if active_exercises in (None, 0, -1):
        body_diagram = static('bodyDiagram/bodyDiagram0.png')
    else:
        body_diagram = static(f'bodyDiagram/bodyDiagram{active_exercises}.png')

    # Загрузка упражнений только из базы данных!
    from app.models import Exercise
    all_exercises = Exercise.objects.all()

    # Фильтрация по группе
    if active_exercises == 0 or active_exercises is None:
        exercise_list = all_exercises
    elif active_exercises == 100:
        exercise_list = all_exercises
    else:
        exercise_list = all_exercises.filter(group_code=active_exercises)

    # Поиск
    search = request.GET.get('search', '').strip().lower()
    if search:
        exercise_list = exercise_list.filter(
            models.Q(name__icontains=search) | models.Q(description__icontains=search)
        )
        active_exercises = -1

    # Формируем список уникальных групп мышц для фильтрации
    all_groups = set()
    all_group_codes = dict()
    for ex in all_exercises:
        all_groups.add((ex.group, ex.group_code))
        all_group_codes[ex.group] = ex.group_code
    muscle_groups = sorted(list(all_groups), key=lambda x: x[1])

    context = {
        'exercises': exercise_list,
        'title': 'Каталог упражнений',
        'active_exercise': active_exercises,
        'classes': classes,
        'body_diagram': body_diagram,
        'muscle_groups': muscle_groups,
    }
    return render(request, 'app/exercises.html', context)

def foodtracker(request):
    if not request.user.is_authenticated:
        return redirect('app:login')
    else:
        # Обработка отправки форм
        if request.method == 'POST' and 'sub_btn_1' in request.POST:
            form_sub = FoodForm(request.POST)
            if form_sub.is_valid():
                # Ensuring calories match description if already in database
                val = True
                if Food_Entry.objects.filter(user=request.user, description=form_sub.cleaned_data['description']).exists():
                    old_entry = Food_Entry.objects.filter(user=request.user, description=form_sub.cleaned_data['description']).first()
                    if old_entry.calories != form_sub.cleaned_data['calories']:
                        messages.error(request, "Ошибка: для одинаковых описаний калорийность должна совпадать!", extra_tags='danger')
                        val = False
                    else:
                        f = Food_Entry(date=form_sub.cleaned_data['date'], description=form_sub.cleaned_data['description'], calories=form_sub.cleaned_data['calories'], user=request.user)
                        f.save()
                # Ensuring calories are 0 or greater
                if form_sub.cleaned_data['calories'] < 0:
                    messages.error(request, "Ошибка: калорий должно быть не меньше 0!", extra_tags='danger')
                    val = False
                if val == True:
                    f = Food_Entry(date=form_sub.cleaned_data['date'], description=form_sub.cleaned_data['description'], calories=form_sub.cleaned_data['calories'], user=request.user)
                    f.save()
                    messages.success(request, "Успешно добавлено: " + form_sub.cleaned_data['description'] + ".", extra_tags='success')
            else:
                messages.error(request, "Ошибка: описание может содержать только буквы, цифры, точки, запятые и скобки!", extra_tags='danger')
        elif request.method == 'POST' and 'sub_btn_2' in request.POST:
            form_sub = FoodFormTheSecond(request.POST, request=request)
            if form_sub.is_valid():
                f = Food_Entry.objects.filter(user=request.user, description=form_sub.cleaned_data['description']).first()
                f.pk = None
                f.date = form_sub.cleaned_data["date"]
                f.save()
                messages.success(request, "Успешно добавлено: " + form_sub.cleaned_data['description'] + ".", extra_tags='success')
        elif request.method == 'POST':
            f = Food_Entry.objects.filter(user=request.user, pk=request.POST['pk']).first()
            Food_Entry.objects.filter(user=request.user, pk=request.POST['pk']).delete()
            if f:
                messages.success(request, "Успешно удалено: " + f.description + ".", extra_tags='success')
            else:
                messages.success(request, "Запись уже удалена.", extra_tags='success')
        # Создание форм
        form = FoodForm()
        form_2 = FoodFormTheSecond(request=request)

        # Получение данных
        entries = Food_Entry.objects.filter(user=request.user).order_by('-date')
        data = {}
        for e in entries:
            if e.date in data:
                data[e.date].append(e)
            else:
                data[e.date] = [e]
        total_calories = {}
        for date in data:
            sum = 0
            for foods in data[date]:
                sum = sum + foods.calories
            total_calories[date] = sum

        # Передача информации
        context = {
            'title': 'Трекер питания',
            'data': data,
            'form': form,
            'form_2': form_2,
            'total_calories': total_calories,
            'today_date': timezone.now().date(),
            'yesterday_date': timezone.now().date() - timedelta(days=1)
        }
        return render(request, 'app/foodtracker.html', context)


def weightlog(request):
    if not request.user.is_authenticated:
        return redirect('app:login')
    else:
        form = WeightLogForm()
        context = {
            'title': 'Весовой журнал',
            'weight_logs': WeightLog.objects.filter(user=request.user).order_by('-timestamp'),
            'form': form,
            'savedWeight': False
        }
        if request.method == 'POST':
            form = WeightLogForm(request.POST)
            if form.is_valid():
                try:
                    weight = float(form.cleaned_data['weight'])
                except (ValueError, TypeError):
                    messages.error(request, "Введите корректное значение веса!", extra_tags='danger')
                    return render(request, 'app/weightlog.html', context)
                if weight < 20 or weight > 400:
                    messages.error(request, "Вес должен быть в диапазоне 20–400 кг!", extra_tags='danger')
                else:
                    last_log = WeightLog.objects.filter(user=request.user).order_by('-timestamp').first()
                    if last_log and abs(weight - float(last_log.weight)) > 10:
                        messages.error(request, f"Внимание: разница с предыдущей записью составляет {abs(weight - float(last_log.weight)):.1f} кг. Проверьте правильность ввода!", extra_tags='danger')
                    else:
                        w = WeightLog(weight=weight, user=request.user)
                        w.save()
                        messages.success(request, "Вес успешно добавлен!", extra_tags='success')
                        return redirect('app:weightlog')
            else:
                messages.error(request, "Введите корректное значение веса!", extra_tags='danger')
        return render(request, 'app/weightlog.html', context)

def login_view(request):
    context = {
        'title': 'Вход'
    }
    return render(request, 'app/login.html', context)

def results(request):
    if not request.user.is_authenticated:
        return redirect('app:login')
    else:
        # График веса
        weight_logs = list(WeightLog.objects.filter(user=request.user).order_by('timestamp'))
        if weight_logs:
            weight_labels = [i.timestamp.date().strftime('%d.%m') for i in weight_logs]
            weight_values = [float(i.weight) for i in weight_logs]
        else:
            weight_labels = []
            weight_values = []

        # График калорий
        food_entries = Food_Entry.objects.filter(user=request.user).order_by('date').extra({'_date': 'Date(date)'}).values('_date').annotate(val=Avg('calories'), count=Count('calories'))
        cal_labels = []
        cal_values = []
        avgCals = 0
        counts = []
        for item in food_entries:
            date = item.get('_date')
            if isinstance(date, str):
                parts = date.split('-')
                cal_labels.append(f"{parts[2]}.{parts[1]}")
            elif hasattr(date, 'strftime'):
                cal_labels.append(date.strftime('%d.%m'))
            else:
                cal_labels.append(str(date))
            cal_values.append(item.get('val') * item.get('count'))
            counts.append(item.get('count'))
            avgCals += item.get('val') * item.get('count')
        if len(cal_labels) > 0:
            avgCals = avgCals / len(cal_labels)
        
        # Вместо графика силы по упражнению — график среднего веса за день
        avg_weight_by_day = {}
        for i, label in enumerate(weight_labels):
            if label not in avg_weight_by_day:
                avg_weight_by_day[label] = []
            avg_weight_by_day[label].append(weight_values[i])
        avg_weight_labels = list(avg_weight_by_day.keys())
        avg_weight_values = [sum(vals)/len(vals) for vals in avg_weight_by_day.values()]

        # График суммарного поднятого веса по дням
        lifted_weight_by_day = {}
        for log in ExerciseLog.objects.filter(user=request.user):
            date_label = log.date.strftime('%d.%m')
            total = 0
            for ex in Exercise_App.objects.filter(exercise_log=log):
                if ex.exercise_weight and ex.num_reps and ex.num_sets:
                    total += float(ex.exercise_weight) * int(ex.num_reps) * int(ex.num_sets)
            lifted_weight_by_day[date_label] = lifted_weight_by_day.get(date_label, 0) + total
        lifted_labels = list(lifted_weight_by_day.keys())
        lifted_values = list(lifted_weight_by_day.values())

        # Метрики
        weightSum = sum(weight_values)
        if weight_values:
            average = '%.2f' % (weightSum / len(weight_values))
            change = float(weight_values[-1]) - float(weight_values[0])
            change = '%.2f' % change
            min_weight = min(weight_values)
            max_weight = max(weight_values)
        else:
            average = '--'
            change = '--'
            min_weight = '--'
            max_weight = '--'
        if cal_values:
            min_cals = min(cal_values)
            max_cals = max(cal_values)
        else:
            min_cals = '--'
            max_cals = '--'

        context = {
            'title': 'Результаты',
            'weight_labels': weight_labels,
            'weight_values': weight_values,
            'cal_labels': cal_labels,
            'cal_values': cal_values,
            'avg_weight_labels': avg_weight_labels,
            'avg_weight_values': avg_weight_values,
            'lifted_labels': lifted_labels,
            'lifted_values': lifted_values,
            'change': change,
            'average': average,
            'avg_cals': avgCals,
            'min_weight': min_weight,
            'max_weight': max_weight,
            'min_cals': min_cals,
            'max_cals': max_cals,
        }
        return render(request, 'app/results.html', context)


def signup(request):
    if request.user.is_authenticated:
        return redirect('app:home')
    else:
        if request.method == "POST":
            form = forms.UserRegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('app:login')
        else:
            form = forms.UserRegistrationForm()

        context = {
            'title': 'Регистрация',
            'form': form
        }
        return render(request, 'app/signup.html', context)


def logout_user(request):
    logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect('app:home')

@login_required
def export_data_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fittrack_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['Тип', 'Дата/Время', 'Описание', 'Значение', 'Калории'])
    # Вес
    for w in WeightLog.objects.filter(user=request.user):
        writer.writerow(['Вес', w.timestamp, '', w.weight, ''])
    # Питание
    for f in Food_Entry.objects.filter(user=request.user):
        writer.writerow(['Питание', f.date, f.description, '', f.calories])
    # Упражнения
    for log in ExerciseLog.objects.filter(user=request.user):
        for ex in Exercise_App.objects.filter(exercise_log=log):
            writer.writerow(['Упражнение', log.date, ex.exercise_ref.name, ex.exercise_weight, ''])
    return response

@login_required
def export_data_json(request):
    data = {
        'weight': list(WeightLog.objects.filter(user=request.user).values()),
        'food': list(Food_Entry.objects.filter(user=request.user).values()),
        'exercises': [
            {
                'date': log.date,
                'exercises': list(Exercise_App.objects.filter(exercise_log=log).values())
            } for log in ExerciseLog.objects.filter(user=request.user)
        ]
    }
    response = HttpResponse(json.dumps(data, ensure_ascii=False, default=str), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="fittrack_data.json"'
    return response

def error_400(request, exception):
    """Обработчик ошибки 400."""
    return render(request, 'app/400.html', status=400)

def error_500(request):
    """Обработчик ошибки 500."""
    return render(request, 'app/500.html', status=500)

def force_500(request):
    """Временное представление для тестирования ошибки 500."""
    return HttpResponseServerError("Искусственно вызванная ошибка 500.")

def force_400(request):
    """Временное представление для тестирования ошибки 400."""
    return HttpResponseBadRequest("Искусственно вызванная ошибка 400.")
