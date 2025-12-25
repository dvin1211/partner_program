from django.conf import settings
from django.shortcuts import render

from apps.partners.models import PartnerActivity
from apps.core.decorators import role_required
from .common import _get_available_projects,_get_connected_projects

@role_required('partner')
def dashboard(request):  
    """Информационная панель партнёра"""
    user = request.user
    
    last_activity = PartnerActivity.objects.filter(partner=user.partner_profile,is_read=False).order_by('-created_at')
    notifications_count = PartnerActivity.objects.filter(partner=user.partner_profile,is_read=False).count()
    available_projects = _get_available_projects(request)     
    connected_projects = _get_connected_projects(request)  
    active_connected_projects = connected_projects.filter(
        partner_memberships__status="Активен"
    ).count()
    clicks_count = user.partner_profile.clicks.count() 
    if clicks_count == 0:
        conversion = 0
    else:
        conversion =  f"{(user.partner_profile.conversions.count() / user.partner_profile.clicks.count()) * 100:.2f}"
    total_projects = available_projects.count()
    
    context = {
        "user": user,  
        "int_balance":int(user.partner_profile.balance),
        "last_activity":last_activity,
        "notifications_count":notifications_count,
        
        "total_projects":total_projects,
        "active_connected_projects": active_connected_projects,
        "clicks_count":clicks_count,
        "conversion":conversion,
        
        "is_payout_available": user.partner_profile.balance > float(settings.PARTNER_PAYOUT_SETTINGS["min_amount"]),
        "min_payout": settings.PARTNER_PAYOUT_SETTINGS["min_amount"],
        "fee_percent": settings.PARTNER_PAYOUT_SETTINGS["fee_percent"],
    }
    
    return render(request, 'partners/dashboard/dashboard.html',context=context)


