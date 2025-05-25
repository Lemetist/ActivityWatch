from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator


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
