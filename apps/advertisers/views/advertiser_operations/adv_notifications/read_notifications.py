from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from apps.advertisers.models import AdvertiserActivity
from apps.core.decorators import role_required


@role_required('advertiser')
@require_POST
def read_advertiser_notifications(request):
    """Прочитать уведомления рекламодателя"""
    advertiser = request.user
    if not hasattr(advertiser,"advertiserprofile"):
        return redirect('index')
    AdvertiserActivity.objects.filter(advertiser=advertiser.advertiserprofile,
        is_read=False
    ).update(is_read=True)
   
    return redirect("advertiser_dashboard")