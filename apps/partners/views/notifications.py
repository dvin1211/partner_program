from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from apps.core.decorators import role_required
from apps.partners.models import PartnerActivity
from apps.tracking.models import Conversion

@role_required('partner')
def notifications(request):  
    """Уведомления партнёра"""
    user = request.user
    
    unread_notifications_count = PartnerActivity.objects.filter(partner=user.partner_profile,is_read=False).count()
    total_notifications_count = PartnerActivity.objects.filter(partner=user.partner_profile).count()
    today_conversions_count = Conversion.objects.filter(partner=user.partner_profile, created_at__date=timezone.now()).count()
    
    
    notifications  = PartnerActivity.objects.filter(partner=user.partner_profile).order_by('-created_at')    
    notifications_page = Paginator(notifications,10)
    
    page = request.GET.get('page', 1)
    
    try:
        notifications_page = notifications_page.page(page)
    except (PageNotAnInteger, EmptyPage):
        notifications_page = notifications_page.page(1)
    context = {
        "user": user,
        
        "notifications":notifications_page,
        "notifications_count":unread_notifications_count,
        "total_notifications_count":total_notifications_count,
        
        "today_conversions_count":today_conversions_count,
    }
    
    return render(request, 'partners/notifications/notifications.html',context=context)


