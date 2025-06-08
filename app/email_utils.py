from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse


def send_password_reset_email(request, user, token):
    """Отправляет email для сброса пароля"""
    try:
        current_site = get_current_site(request)
        
        # Формируем ссылку для сброса пароля
        reset_url = request.build_absolute_uri(
            reverse('app:password_reset_confirm', kwargs={
                'uidb64': token['uidb64'],
                'token': token['token']
            })
        )
        
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': current_site.name,
        }
        
        html_message = render_to_string('app/email/password_reset_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Восстановление пароля - ActivityWatch',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки email для сброса пароля: {e}")
        return False
