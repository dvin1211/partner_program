from django.shortcuts import render

from apps.advertisers.models import AdvertiserActivity
from apps.core.decorators import role_required


@role_required('advertiser')
def requisites(request):
    """Страница с настройками юр. данных рекламодателя"""
    user = request.user
    
    notifications_count = AdvertiserActivity.objects.filter(advertiser=user.advertiserprofile,is_read=False).count()
    
    context = {
        "notifications_count":notifications_count
    }
    
    return render(request, 'advertisers/requisites/requisites.html',context=context)