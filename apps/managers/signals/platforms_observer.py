from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from apps.partners.models import Platform
from apps.managers.models import ManagerActivity, ManagerProfile


@receiver(post_save,sender=Platform)
def make_notification_on_platform(sender,instance,created, **kwargs):
    """
    Уведомления при создании/обновлении платформы партнёра
    
    :param sender: Класс отправителя сигнала
    :param instance: Конкретный объект отправителя сигнала
    :param created: Создан или обновлен объект (True/False)
    :param kwargs: доп. параметры 
    """

    if created:
        managers = ManagerProfile.objects.all()
        notifications = []
        for manager in managers:
            obj = ManagerActivity(
                manager=manager,
                activity_type = ManagerActivity.ActivityType.PLATFORM,
                title='Новая платформа',
                details=f'Партнёр: {instance.partner.username}' 
            )
            notifications.append(obj)

        ManagerActivity.objects.bulk_create(notifications,batch_size=1000)