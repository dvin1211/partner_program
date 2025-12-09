from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from apps.partners.models import PartnerTransaction
from apps.managers.models import ManagerActivity, ManagerProfile


@receiver(post_save,sender=PartnerTransaction)
def make_notification_on_partner_payout(sender,instance,created, **kwargs):
    if created:
        managers = ManagerProfile.objects.all()
        notifications = []
        for manager in managers:
            obj = ManagerActivity(
                manager=manager,
                activity_type = ManagerActivity.ActivityType.PAYOUT,
                title='Запрос на выплату средств',
                details=f'Партнёр: {instance.partner.username}' 
            )
            notifications.append(obj)

        ManagerActivity.objects.bulk_create(notifications,batch_size=1000)