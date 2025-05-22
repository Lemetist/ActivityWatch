# models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import RegexValidator
from app.models import Exercise as ExerciseReference


class ExerciseLog(models.Model) :
    """
    Модель журнала упражнений.

    Атрибуты:
        user (User): Пользователь, связанный с журналом.
        date (date): Дата записи журнала.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    duration = models.PositiveIntegerField(null=True, blank=True, verbose_name='Длительность (мин)')
    note = models.TextField(null=True, blank=True, verbose_name='Заметка')

    def __str__(self) :
        """
        Возвращает строковое представление журнала.
        """
        return str(self.user) + "\t" + str(self.date)

    def get_absolute_url(self) :
        """
        Возвращает абсолютный URL для просмотра журнала.
        """
        return reverse('exlog-detail', kwargs={'pk' : self.pk})


class Exercise(models.Model) :
    """
    Модель упражнения.
    Теперь ссылается на справочник Exercise из app.models.

    Атрибуты:
        exercise_log (ExerciseLog): Журнал, связанный с упражнением.
        exercise_ref (ExerciseReference): Справочник упражнения.
        num_sets (int): Количество подходов.
        num_reps (int): Количество повторений.
        exercise_weight (int): Вес для упражнения.
    """
    exercise_log = models.ForeignKey(ExerciseLog, on_delete=models.CASCADE)
    exercise_ref = models.ForeignKey(ExerciseReference, on_delete=models.CASCADE, verbose_name='Упражнение')
    num_sets = models.PositiveIntegerField()
    num_reps = models.PositiveIntegerField()
    exercise_weight = models.PositiveIntegerField()

    def __str__(self) :
        """
        Возвращает строковое представление упражнения.
        """
        return f"{self.exercise_log} | {self.exercise_ref.name} | {self.num_sets}x{self.num_reps} {self.exercise_weight}кг"

    def get_absolute_url(self) :
        """
        Возвращает абсолютный URL для просмотра журнала, связанного с упражнением.
        """
        return reverse('exlog-detail', kwargs={'pk' : self.exercise_log.id})