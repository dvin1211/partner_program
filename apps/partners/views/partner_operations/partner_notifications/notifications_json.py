from django.utils.timesince import timesince
from django.utils.timezone import now
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from apps.core.decorators import role_required
from apps.partners.models import PartnerActivity


@role_required('partner')
@require_GET
def notifications_json(request):
    partner = request.user.partner_profile

    qs = PartnerActivity.objects.filter(partner=partner).order_by('-created_at')
    
    page = request.GET.get('page', 1)

    paginator = Paginator(qs, 10)

    try:
        notifications_page = paginator.page(page)
    except (EmptyPage,PageNotAnInteger):
        notifications_page = paginator.page(1)

    notifications = []
    for obj in notifications_page:
        notifications.append({
            "id": obj.id,
            "activity_type": obj.activity_type,
            "activity_type_display": obj.get_activity_type_display(),
            "title": obj.title,
            "details": obj.details,
            "is_read": obj.is_read,
            "created_at": f"{timesince(obj.created_at, now())} назад",
        })

    return JsonResponse({
        "notifications_count": qs.count(),
        "num_pages": paginator.num_pages, 
        "current_page": notifications_page.number, 
        "notifications": notifications,
    })
