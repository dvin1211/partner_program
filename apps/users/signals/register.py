from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from utils import send_email_via_mailru

User = get_user_model()

EMAIL_TEXTS = {
    'partner': {
        'subject': '🎉 Добро пожаловать в партнёрскую программу LinkOffer!',
        'message': 'Здравствуйте.\nБлагодарим вас за регистрацию в нашей партнёрской программе.\nТеперь вы можете зарабатывать, продвигая проекты рекламодателей.'
    },
    'advertiser': {
        'subject': '🎉 Добро пожаловать в партнёрскую программу LinkOffer!',
        'message': 'Здравствуйте.\nБлагодарим вас за регистрацию в нашей партнёрской программе.\nТеперь вы можете продвигать свои проекты и привлекать новых клиентов.'
    }
}

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """Отправка приветственного письма при создании пользователя"""
    
    if not created:
        return
    
    user_type = getattr(instance, 'user_type', None)
    
    if user_type not in EMAIL_TEXTS:
        return
    
    email = instance.email

    transaction.on_commit(
        lambda: send_email_via_mailru.delay(email, EMAIL_TEXTS[user_type]['message'],EMAIL_TEXTS[user_type]['subject'])
    )
