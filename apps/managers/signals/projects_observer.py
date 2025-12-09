from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from apps.advertisers.models import Project
from apps.managers.models import ManagerActivity, ManagerProfile


@receiver(post_save,sender=Project)
def make_notification_on_project(sender,instance,created, **kwargs):
    """
    Уведомления при создании/обновлении проекта рекламодателя
    
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
                activity_type = ManagerActivity.ActivityType.PROJECT,
                title='Новый проект',
                details=f'Рекламодатель: {instance.advertiser.username}' 
            )
            notifications.append(obj)

        ManagerActivity.objects.bulk_create(notifications,batch_size=1000)