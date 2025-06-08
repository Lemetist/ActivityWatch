from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app.models import EmailVerificationToken


class Command(BaseCommand):
    help = 'Удаляет истёкшие токены верификации email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Удалить токены старше указанного количества дней (по умолчанию 1 день)',
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        expired_tokens = EmailVerificationToken.objects.filter(created_at__lt=cutoff_date)
        count = expired_tokens.count()
        
        expired_tokens.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно удалено {count} истёкших токенов верификации')
        )
