from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages


from apps.core.decorators import role_required
from apps.partners.models import Platform, PartnerActivity
from utils import send_email_via_mailru

@role_required('manager')
@require_POST
def approve_platform(request, platform_id):
    platform = get_object_or_404(Platform,id=platform_id)
    platform.status = 'Подтверждено'
    platform.save()
    if platform.partner.email_notifications:
        try:
            send_email_via_mailru.delay(platform.partner.email,f"Платформа {platform.name} была одобрена модератором", 'Уведомление о подтверждении платформы')
        except:
            pass
    PartnerActivity.objects.create(
        partner=platform.partner.partner_profile,
        activity_type='approve',
        title='Платформа одобрена',
        details=f'{platform.name} была одобрена модератором'
    )
    messages.success(request,message=f"Платформа {platform.name} была одобрена",extra_tags="approve_success")
    return redirect("manager_platforms")