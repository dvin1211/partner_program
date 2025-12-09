from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from apps.advertisers.models import AdvertiserProfile
from apps.managers.models import ManagerActivity, ManagerProfile
from apps.partners.models import PartnerProfile


@receiver(post_save,sender=AdvertiserProfile)
def make_notification_on_register_advertiser(sender,instance,created, **kwargs):
    if created:
        managers = ManagerProfile.objects.all()
        notifications = []
        for manager in managers:
            obj = ManagerActivity(
                manager=manager,
                activity_type = ManagerActivity.ActivityType.NEW_USER,
                title='Зарегистрирован новый рекламодатель',
                details=f'Логин: {instance.user.username}' 
            )
            notifications.append(obj)

        ManagerActivity.objects.bulk_create(notifications,batch_size=1000)



@receiver(post_save,sender=PartnerProfile)
def make_notification_on_register_partner(sender,instance,created, **kwargs):
    if created:
        managers = ManagerProfile.objects.all()
        notifications = []
        for manager in managers:
            obj = ManagerActivity(
                manager=manager,
                activity_type = ManagerActivity.ActivityType.NEW_USER,
                title='Зарегистрирован новый партнёр',
                details=f'Логин: {instance.user.username}' 
            )
            notifications.append(obj)

        ManagerActivity.objects.bulk_create(notifications,batch_size=1000)



@receiver(post_save,sender=ManagerProfile)
def make_notification_on_register_manager(sender,instance,created, **kwargs):
    if created:
        managers = ManagerProfile.objects.all()
        notifications = []
        for manager in managers:
            obj = ManagerActivity(
                manager=manager,
                activity_type = ManagerActivity.ActivityType.NEW_USER,
                title='Зарегистрирован новый менеджер',
                details=f'Логин: {instance.user.username}' 
            )
            notifications.append(obj)

        ManagerActivity.objects.bulk_create(notifications,batch_size=1000)