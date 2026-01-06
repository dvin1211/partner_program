from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.core.decorators import role_required
from apps.users.models import User
from apps.advertisers.models import AdvertiserActivity
from apps.partners.models import PartnerActivity
from utils import send_email_via_mailru


@role_required('manager')
@require_POST
def make_single_notification(request,user_id):
    """Отправить сообщение одному пользователю"""
    selected_user = User.objects.get(id=user_id)
    
    msg_title = request.POST.get('send-msg-theme')
    msg_text = request.POST.get('send-msg-text')

    if 'send-msg-website' in request.POST:
        if selected_user.user_type == 'advertiser':
            notification = AdvertiserActivity(
                advertiser = selected_user.advertiserprofile,
                activity_type=AdvertiserActivity.ActivityType.SYSTEM,
                title=msg_title,
                details = msg_text
            )
            notification.save()
        elif selected_user.user_type == 'partner':
            notification = PartnerActivity(
                partner=selected_user.partner_profile,
                activity_type=AdvertiserActivity.ActivityType.SYSTEM,
                title=msg_title,
                details = msg_text
            )
            notification.save()
    if 'send-msg-email' in request.POST:
        send_email_via_mailru.delay(selected_user.email, msg_text, msg_title)
    print(request.POST)
    return JsonResponse({"success":True},status=200)
