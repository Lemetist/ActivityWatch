from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.db.models import Sum
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    group = models.CharField(max_length=100)
    group_code = models.IntegerField(null=True, blank=True, default=0)  # Сделано необязательным
    description = models.TextField()
    image_link = models.ImageField(upload_to='exerciseImages/', null=True, blank=True)  # Поле для загрузки изображений
    ex_id = models.IntegerField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.ex_id:
            # Автоматическое назначение ex_id, если оно не задано
            max_ex_id = Exercise.objects.aggregate(models.Max('ex_id'))['ex_id__max']
            self.ex_id = (max_ex_id or 0) + 1
        super().save(*args, **kwargs)


class WeightLog(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    weight = models.CharField(max_length=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.timestamp) + ' ' + self.user.username


class Food_Entry(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=31)
    calories = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.description

class Goal(models.Model):
    GOAL_TYPE_CHOICES = [
        ('weight', 'Вес'),
        ('workouts', 'Тренировки'),
        ('calories', 'Калории'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Название цели')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default='weight', verbose_name='Тип цели')
    target_value = models.FloatField(verbose_name='Целевое значение')
    current_value = models.FloatField(default=0, verbose_name='Текущее значение')
    unit = models.CharField(max_length=20, default='', verbose_name='Единица измерения')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True, verbose_name='Желаемая дата достижения')
    is_achieved = models.BooleanField(default=False, verbose_name='Достигнута')

    def __str__(self):
        return f"{self.user.username}: {self.name} ({self.goal_type})"

    @property
    def is_goal_achieved(self):
        """Проверяет, достигнута ли цель на основе current_value и target_value"""
        return self.current_value >= self.target_value

    def save(self, *args, **kwargs):
        """Переопределяем метод save для автоматического обновления статуса достижения"""
        # Обновляем статус достижения цели при каждом сохранении
        self.is_achieved = self.current_value >= self.target_value
        super().save(*args, **kwargs)

    def update_current_value(self):
        """Обновляет текущее значение цели на основе данных пользователя"""
        if self.goal_type == 'weight':
            # Получаем последнюю запись веса
            latest_weight = WeightLog.objects.filter(user=self.user).order_by('-timestamp').first()
            if latest_weight:
                try:
                    self.current_value = float(latest_weight.weight)
                except (ValueError, TypeError):
                    self.current_value = 0
        elif self.goal_type == 'workouts':
            # Подсчитываем количество тренировок за текущий месяц
            from django.utils import timezone
            from datetime import datetime, timedelta
            start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            workouts_count = ExerciseLog.objects.filter(
                user=self.user,
                timestamp__gte=start_of_month
            ).count()
            self.current_value = workouts_count
        elif self.goal_type == 'calories':
            # Подсчитываем калории за сегодня
            from django.utils import timezone
            today = timezone.now().date()
            today_calories = Food_Entry.objects.filter(
                user=self.user,
                date=today
            ).aggregate(total=models.Sum('calories'))['total'] or 0
            self.current_value = today_calories
        
        # Обновляем статус достижения цели
        self.is_achieved = self.current_value >= self.target_value
        self.save()

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'


# Сигналы для автоматического обновления целей
@receiver(post_save, sender='app.WeightLog')
def update_weight_goals(sender, instance, created, **kwargs):
    """Обновляем цели типа 'вес' при добавлении новой записи веса"""
    if created:
        weight_goals = Goal.objects.filter(user=instance.user, goal_type='weight')
        for goal in weight_goals:
            goal.update_current_value()


@receiver(post_save, sender='exlog_app.ExerciseLog')
def update_workout_goals(sender, instance, created, **kwargs):
    """Обновляем цели типа 'тренировки' при добавлении новой тренировки"""
    if created:
        workout_goals = Goal.objects.filter(user=instance.user, goal_type='workouts')
        for goal in workout_goals:
            goal.update_current_value()


@receiver(post_save, sender='app.Food_Entry')
def update_calorie_goals(sender, instance, created, **kwargs):
    """Обновляем цели типа 'калории' при добавлении новой записи питания"""
    if created:
        calorie_goals = Goal.objects.filter(user=instance.user, goal_type='calories')
        for goal in calorie_goals:
            goal.update_current_value()
