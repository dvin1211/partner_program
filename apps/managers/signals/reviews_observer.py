from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from apps.core.models import UserReview
from apps.managers.models import ManagerActivity, ManagerProfile


@receiver(post_save,sender=UserReview)
def make_notification_on_review(sender,instance,created, **kwargs):
    if created:
        managers = ManagerProfile.objects.all()
        notifications = []
        if instance.user:
            details_msg = f'От: {instance.user.username}'
        else:
            details_msg = f'От анонима'
        for manager in managers:
            obj = ManagerActivity(
                manager=manager,
                activity_type = ManagerActivity.ActivityType.REVIEW,
                title=f'Новый отзыв #{instance.id}',
                details=details_msg
            )
            notifications.append(obj)

        ManagerActivity.objects.bulk_create(notifications,batch_size=1000)
