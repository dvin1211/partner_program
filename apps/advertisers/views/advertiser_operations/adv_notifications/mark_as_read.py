from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.advertisers.models import AdvertiserActivity
from apps.core.decorators import role_required


@role_required('advertiser')
@require_POST
def mark_notification_read(request, notification_id):
    """
    Отметить одно уведомление как прочитанное
    """
    advertiser = request.user.advertiserprofile
    try:
        notification = AdvertiserActivity.objects.get(id=notification_id, advertiser=advertiser)
        notification.is_read = True
        notification.save()
        return JsonResponse({"success": True, "notification_id": notification_id})
    except AdvertiserActivity.DoesNotExist:
        return JsonResponse({"success": False, "error": "Уведомление не найдено"}, status=404)