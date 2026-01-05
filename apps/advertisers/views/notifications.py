from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from apps.advertisers.models import AdvertiserActivity
from apps.core.decorators import role_required
from apps.tracking.models import Conversion


@role_required('advertiser')
def notifications(request):  
    """Уведомления рекламодателя"""
    user = request.user
    user.advertiserprofile.is_complete_profile()
    
    unread_notifications_count = AdvertiserActivity.objects.filter(advertiser=user.advertiserprofile,is_read=False).count()
    total_notifications_count = AdvertiserActivity.objects.filter(advertiser=user.advertiserprofile).count()
    today_conversions_count = Conversion.objects.filter(advertiser=user.advertiserprofile, created_at__date=timezone.now()).count()
    
    
    notifications  = AdvertiserActivity.objects.filter(advertiser=user.advertiserprofile).order_by('-created_at')    
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
    
    return render(request, 'advertisers/notifications/notifications.html',context=context)


