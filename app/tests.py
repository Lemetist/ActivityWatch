from django.test import TestCase
from django.urls import reverse
from .models import Exercise
from django.http import HttpResponseBadRequest

class ExerciseModelTest(TestCase):

    def setUp(self):
        self.exercise = Exercise.objects.create(
            name="Push-ups",
            group="Chest",
            description="An exercise for chest muscles.",
            image_link="exerciseImages/pushups.jpg",
        )

    def test_exercise_creation(self):
        """Проверка, что объект Exercise создается корректно."""
        self.assertEqual(self.exercise.name, "Push-ups")
        self.assertEqual(self.exercise.group, "Chest")
        self.assertEqual(self.exercise.description, "An exercise for chest muscles.")
        self.assertTrue(self.exercise.image_link)

    def test_group_code_assignment(self):
        """Проверка автоматического назначения group_code."""
        self.assertIsNotNone(self.exercise.group_code)

    def test_ex_id_assignment(self):
        """Проверка автоматического назначения ex_id."""
        self.assertIsNotNone(self.exercise.ex_id)

class ErrorViewTest(TestCase):

    def test_400_error(self):
        """Проверка использования шаблона 400.html."""
        response = self.client.get('/force-400/')  # URL, вызывающий ошибку 400
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'app/400.html')

    def test_500_error(self):
        """Проверка использования шаблона 500.html."""
        with self.settings(DEBUG=False):  # Убедитесь, что DEBUG отключен
            response = self.client.get('/force-500/')  # URL, вызывающий ошибку 500
            self.assertEqual(response.status_code, 500)
            self.assertTemplateUsed(response, 'app/500.html')
