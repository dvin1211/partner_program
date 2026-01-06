from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST

from apps.core.decorators import role_required
from apps.partnerships.models import ProjectPartner
from utils import send_email_via_mailru

@role_required('partner')
@require_POST
@transaction.atomic
def resume_partnership(request,project_id):
    """ Воозобновить сотрудничество партнёра с проектом рекламодателя. Для партнёра"""
    partnership = get_object_or_404(ProjectPartner,partner=request.user,project=project_id)
    partnership.status = "Активен"
    partnership.suspension_reason = None 
    partnership.suspension_comment = None
    partnership.save()
    
    title = f'✅ Возобновление сотрудничества'
    message = f"""Партнёр {partnership.partner} снова продвигает ваш проект «{partnership.project.name}».  

После возобновления сотрудничества у вас будут учитываться конверсии/переходы.
Это письмо отправлено автоматически."""
    if partnership.advertiser.email_notifications:
        send_email_via_mailru.delay(partnership.advertiser.email,message,title)
    messages.success(request,message="Сотрудничество с рекламодателем успешно возобновлено!",extra_tags="resume_partnership_success")
    return redirect('partner_connections')