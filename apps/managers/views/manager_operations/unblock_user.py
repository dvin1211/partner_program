from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from apps.users.models import User
from utils import send_email_via_mailru


message = f"""Здравствуйте, уважаемый пользователь.\n    
Рады сообщить, что ваш аккаунт был успешно разблокирован.
Теперь вы снова можете пользоваться всеми возможностями сервиса."""


@login_required
@require_POST
def unblock_user(request, user_id):
    user = get_object_or_404(User,id=user_id)
    user.unblock()
    
    try:
        send_email_via_mailru.delay(user.email,message,'Ваш аккаунт разблокирован')
    except:
        pass
    messages.success(request,message=f'Пользователь {user.username} (ID: {user.id}) был разблокирован',extra_tags="unblock_user_success")
    return redirect('manager_users')