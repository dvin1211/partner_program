from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages


from apps.core.decorators import role_required
from apps.partners.models import Platform, PartnerActivity
from utils import send_email_via_mailru


@role_required('manager')
@require_POST
def reject_platform(request, platform_id):
    platform = get_object_or_404(Platform,id=platform_id)
    platform.status = 'Отклонено'
    platform.is_active = False
    platform.save()
    reason = request.POST.get('moderation_rejection_reason')
    if platform.partner.email_notifications:
        try:
            send_email_via_mailru.delay(platform.partner.email,f"Платформа {platform.name} была отклонена модератором по причине: {reason}", 'Уведомление об отклонении платформы')
        except:
            pass
    PartnerActivity.objects.create(
        partner=platform.partner.partner_profile,
        activity_type='reject',
        title='Платформа отклонена',
        details=f'{platform.name} была отклонена модератором. Причина: {reason}'
    )
    messages.success(request,message=f"Платформа {platform.name} была отклонена",extra_tags="reject_success")
    return redirect("manager_platforms")
