from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST

from apps.core.decorators import role_required
from apps.partnerships.models import ProjectPartner
from utils import send_email_via_mailru

@role_required('partner')
@require_POST
@transaction.atomic
def suspend_partnership(request,project_id):
    """Приостановить сотрудничество партнёра с проектом рекламодателя. Для партнёра"""
    partnership = ProjectPartner.objects.get(partner=request.user,project=project_id)
    partnership.status = "Приостановлен"
    partnership.suspension_reason = request.POST.get('suspension_reason',None)
    partnership.suspension_comment = request.POST.get('suspension_comment',None)
    partnership.save()
    
    title = '❌ Приостановление сотрудничества'
    message = f"""Уважаемый рекламодатель,
Сообщаем вам, что партнёр {partnership.partner} временно прекратил сотрудничество по проекту «{partnership.project.name}» временно приостановлено.
Причина: {request.POST.get('suspension_reason',"Не указана")}
Комментарий: {request.POST.get('suspension_comment',"Не указан")}

В период приостановки:
- Новые клики/конверсии не будут учитываться
- Доступ к статистике сохранится в режиме просмотра

Это письмо отправлено автоматически."""
    
    if partnership.advertiser.email_notifications:
        send_email_via_mailru.delay(partnership.advertiser.email,message,title)
    messages.success(request,message="Сотрудничество с рекламодателем успешно приостановлено!",extra_tags="suspend_partnership_success")
    return redirect('partner_connections')