from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.advertisers.models import AdvertiserActivity
from apps.core.decorators import role_required


@role_required('advertiser')
@require_POST
def mark_all_notifications_read(request):
    """
    Отметить все уведомления пользователя как прочитанные
    """
    advertiser = request.user.advertiserprofile
    AdvertiserActivity.objects.filter(advertiser=advertiser, is_read=False).update(is_read=True)
    return JsonResponse({"success": True})