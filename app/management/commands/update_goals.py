from django.core.management.base import BaseCommand
from app.models import Goal


class Command(BaseCommand):
    help = 'Обновляет текущие значения для всех целей'

    def handle(self, *args, **options):
        goals = Goal.objects.all()
        updated_count = 0
        achieved_count = 0
        
        for goal in goals:
            old_value = goal.current_value
            old_achieved = goal.is_achieved
            goal.update_current_value()
            
            if goal.current_value != old_value or goal.is_achieved != old_achieved:
                updated_count += 1
                status_changed = ""
                if goal.is_achieved != old_achieved:
                    status_changed = f" [Статус: {'Достигнута' if goal.is_achieved else 'В процессе'}]"
                    if goal.is_achieved:
                        achieved_count += 1
                
                self.stdout.write(
                    f"Цель '{goal.name}' пользователя {goal.user.username}: "
                    f"{old_value} → {goal.current_value}{status_changed}"
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Обновлено {updated_count} целей из {goals.count()}. '
                f'Достигнуто целей: {achieved_count}'
            )
        )
