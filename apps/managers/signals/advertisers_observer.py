from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from apps.advertisers.models import AdvertiserTransaction
from apps.managers.models import ManagerActivity, ManagerProfile


@receiver(post_save,sender=AdvertiserTransaction)
def make_notification_on_advertiser_topup(sender,instance,created, **kwargs):
    if created:
        managers = ManagerProfile.objects.all()
        notifications = []
        for manager in managers:
            obj = ManagerActivity(
                manager=manager,
                activity_type = ManagerActivity.ActivityType.TOPUP,
                title='Запрос на пополнение баланса',
                details=f'Рекламодатель: {instance.advertiser.user.username}' 
            )
            notifications.append(obj)

        ManagerActivity.objects.bulk_create(notifications,batch_size=1000)