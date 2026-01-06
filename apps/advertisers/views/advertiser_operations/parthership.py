from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST
from django.utils.timezone import now

from apps.core.decorators import role_required
from apps.users.models import User
from apps.partnerships.models import ProjectPartner
from utils import send_email_via_mailru


@role_required('advertiser')
@require_POST
@transaction.atomic
def stop_partnership_with_partner(request,partner_id):
    """Остановить сотрудничество рекламодателя с партнёром (Со всеми подключенными проектами). Для рекламодателя"""
    
    
    partnership = ProjectPartner.objects.filter(
        advertiser=request.user,
        partner=partner_id
    )
    
    if not partnership.exists():
        messages.error(request, "Сотрудничество с данным партнёром не найдено.",extra_tags="stop_partnership_error")
        return redirect('advertiser_partners')
    
    user = User.objects.get(id=partner_id)
    partnership.delete()
    date_str = now().strftime("%d.%m.%Y %H:%M")
    
    title = "❌ Остановка сотрудничества"
    message = f"""Здравствуйте,{user.username}!
    
    
Рекламодатель {request.user.username} прекратил сотрудничество с вами {date_str}.\n\n\n
С уважением,\nКоманда поддержки"""
    if user.email_notifications:
        send_email_via_mailru.delay(user.email,message,title)
    messages.success(request,message="Сотрудничество с партнёром успешно остановлено!",extra_tags="stop_partnership_success")
    return redirect('advertiser_partners')