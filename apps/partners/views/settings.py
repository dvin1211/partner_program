from django.shortcuts import render

from apps.core.decorators import role_required
from apps.partners.models import PartnerActivity


@role_required('partner')
def settings(request):  
    """Настройки партнёра"""
    user = request.user
    if not user.profile_completed:
        user.partner_profile.is_complete_profile()
        
    notifications_count = PartnerActivity.objects.filter(partner=user.partner_profile,is_read=False).count()
    
    context = {
        'notifications_count':notifications_count
    }
    
    return render(request, 'partners/settings/settings.html',context=context)