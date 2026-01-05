from django.shortcuts import render

from apps.core.decorators import role_required
from apps.advertisers.forms import ApiSettingsForm
from apps.advertisers.models import AdvertiserActivity


@role_required('advertiser')
def settings(request):
    """Настройки рекламодателя"""
    
    user = request.user
    user.advertiserprofile.is_complete_profile()
    
    notifications_count = AdvertiserActivity.objects.filter(advertiser=user.advertiserprofile,is_read=False).count()
    
    
    context = {
        "notifications_count":notifications_count,
        "apiSettingsForm": ApiSettingsForm(request=request)
    }
    return render(request, 'advertisers/settings/settings.html',context=context)