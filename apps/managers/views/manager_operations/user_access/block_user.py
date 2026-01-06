from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.core.decorators import role_required
from apps.users.models import User
from utils import send_email_via_mailru

@role_required('manager')
@require_POST
def block_user(request, user_id):
    user = User.objects.get(id=user_id)
    duration = request.POST['block_duration']
    durations = {
        '1d':1,
        '7d':7,
        '30d':30,
        'perm':None
    }
    duration_cases = {
        '1d':"на 1 день",
        '7d':"на 7 дней",
        '30d':"на 1 месяц",
        'perm':"навсегда"
    }
    user.blocking_reason = request.POST['block_reason']
    user.block(durations.get(duration))
    
    blocking_type = "навсегда" if not user.block_until else "временно"
    message = f"""Здравствуйте, {user.get_full_name()}\n
Мы вынуждены сообщить, что ваш аккаунт был {blocking_type} заблокирован модератором по причине {user.blocking_reason}.
Если вы считаете, что произошла ошибка, вы можете связаться с нами для рассмотрения ситуации."""
    try:
        send_email_via_mailru.delay(recipient=user.email,message=message,subject='Уведомление о блокировке аккаунта')
    except:
        pass
    messages.success(request,message=f'Пользователь {user.get_full_name()} (ID: {user.id}) был заблокирован {duration_cases.get(duration)}',extra_tags="block_user_success")
    return redirect('manager_users')