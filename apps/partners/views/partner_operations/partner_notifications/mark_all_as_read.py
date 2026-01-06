from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.core.decorators import role_required
from apps.partners.models import PartnerActivity

@role_required('partner')
@require_POST
def mark_all_notifications_read(request):
    """
    Отметить все уведомления пользователя как прочитанные
    """
    partner = request.user.partner_profile
    PartnerActivity.objects.filter(partner=partner, is_read=False).update(is_read=True)
    return JsonResponse({"success": True})