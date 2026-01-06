from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

@login_required
@require_POST
def update_password(request):
    """Изменить пароль пользователя"""
    user = request.user
    
    redirect_to = None
    if hasattr(user, "advertiserprofile"):
        redirect_to = 'advertiser_settings'
    elif hasattr(user, "partner_profile"):
        redirect_to = 'partner_settings'
    elif hasattr(user, 'managerprofile'):
        redirect_to = 'manager_settings'
    else:
        redirect_to = 'dashboard'
    
    def error_redirect(message):
        messages.error(request, message=message, extra_tags="password_update_error")
        return redirect(redirect_to)
    
    curr_password = request.POST.get('old_password')
    if not user.check_password(curr_password):
        return error_redirect("Текущий пароль введен неверно.")
    
    new_password = request.POST.get("password1")
    new_password2 = request.POST.get("password2")
    
    if new_password != new_password2:
        return error_redirect("Пароли не совпадают.")
    
    if new_password == curr_password:
        return error_redirect("Новый пароль не может совпадать со старым.")
    
    if len(new_password) < 8:
        return error_redirect("Пароль должен содержать минимум 8 символов.")
    
    # Обновление пароля
    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request, user)
    
    messages.success(request, message="Пароль успешно изменен!", extra_tags="password_update_success")
    return redirect(redirect_to)