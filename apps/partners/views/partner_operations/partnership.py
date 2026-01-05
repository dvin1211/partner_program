from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST

from apps.partnerships.models import ProjectPartner
from utils import send_email_via_mailru

@login_required
@require_POST
@transaction.atomic
def stop_partnership_with_project(request,project_id):
    """Остановить сотрудничество партнёра с проектом рекламодателя. Для партнёра"""
    partnership = get_object_or_404(ProjectPartner,partner=request.user,project=project_id)
    partnership.delete()
    
    title = '❌ Остановка сотрудничества'
    message = f"""Уважаемый рекламодатель,
сообщаем вам, что партнёр {partnership.partner} прекратил сотрудничество по проекту «{partnership.project.name}»\n
Причина: {request.POST.get('suspension_reason', "Не указана")}\n
Комментарий: {request.POST.get('suspension_comment', "Не указан")}
**Что это значит:**  
- Все ссылки партнёра деактивированы  
- Новые переходы с его ресурсов не учитываются  
- Статистика доступна в личном кабинете\n\n
Это письмо отправлено автоматически."""    

    if partnership.advertiser.email_notifications:
        send_email_via_mailru.delay(partnership.advertiser.email,message,title)
    messages.success(request,message="Сотрудничество с рекламодателем успешно остановлено!",extra_tags="stop_partnership_success")
    return redirect('partner_connections')

@login_required
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


@login_required
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