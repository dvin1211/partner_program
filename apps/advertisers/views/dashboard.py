from django.shortcuts import render
from django.conf import settings

from apps.advertisers.models import Project,AdvertiserActivity
from apps.core.decorators import role_required
from apps.tracking.models import Conversion
from apps.users.models import User


@role_required('advertiser')
def dashboard(request):  
    """Информационная панель рекламодателя"""
    user = request.user
    user.advertiserprofile.is_complete_profile()

    partners = User.objects.filter(
        project_memberships__project__advertiser=user
    ).distinct().count()
    projects = Project.objects.filter(
        advertiser=user
    ).filter(status='Подтверждено').count()
    conversions = Conversion.objects.filter(advertiser=user.advertiserprofile).count()
    last_activity = AdvertiserActivity.objects.filter(advertiser=user.advertiserprofile,is_read=False).order_by('-created_at')
    
    notifications_count = AdvertiserActivity.objects.filter(advertiser=user.advertiserprofile,is_read=False).count()
    
    context = {
        "user": user,
        "partners_count": partners,
        "user_projects_count": projects,
        "conversions_count":conversions,
        
        "last_activity":last_activity,
        "notifications_count":notifications_count,
        "min_payout": settings.PARTNER_PAYOUT_SETTINGS["min_amount"],
        "fee_percent": settings.PARTNER_PAYOUT_SETTINGS["fee_percent"],
        
    }
    return render(request, 'advertisers/dashboard/dashboard.html',context=context)