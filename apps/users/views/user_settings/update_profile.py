from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from utils.is_russian_text import is_valid_russian_text


@login_required
@require_POST
def update_profile(request):
    """Обновление профиля с выводом ВСЕХ ошибок"""
    
    user = request.user
    
    new_first_name = request.POST.get('first_name', '')
    new_middle_name = request.POST.get('middle_name','')
    new_last_name = request.POST.get('last_name', '')
    new_email = request.POST.get('email', '').strip()
    new_phone = request.POST.get('phone', '').strip()
    new_description = request.POST.get('description', '')

    redirect_to = None
    if hasattr(user, "advertiserprofile"):
        redirect_to = 'advertiser_settings'
    elif hasattr(user, "partner_profile"):
        redirect_to = 'partner_settings'
    elif hasattr(user, 'managerprofile'):
        redirect_to = 'manager_settings'
    else:
        redirect_to = 'dashboard'
        
    # Все ли значения введены верно
    is_correct = (
        new_first_name.isalpha() and 
        new_last_name.isalpha() and 
        new_middle_name.isalpha()
    )

    if not is_correct:
        messages.error(request,message="ФИО должны содержать только буквы", extra_tags="profile_update_error")
        return redirect(redirect_to)
    
    is_russian_text = (
        is_valid_russian_text(new_first_name) and
        is_valid_russian_text(new_last_name)
    )
    
    if not is_russian_text:
        messages.error(request,message="ФИО должны быть на русском языке", extra_tags="profile_update_error")
        return redirect(redirect_to)

    # Проверяем, есть ли изменения
    has_changes = (
        user.first_name != new_first_name or
        user.middle_name != new_middle_name or
        user.last_name != new_last_name or
        user.email != new_email or
        user.phone != new_phone or
        user.description != new_description
    )

    if not has_changes:
        messages.info(request, message="Данные не изменены", extra_tags="profile_update_error")
        return redirect(redirect_to)

    try:
        # Получаем данные из запроса
        user.first_name = new_first_name
        user.middle_name = new_middle_name
        user.last_name = new_last_name
        user.email = new_email
        user.phone = new_phone
        user.description = new_description

        # Валидация модели перед сохранением
        user.full_clean()
        user.save()
        
        messages.success(request, message="Профиль успешно обновлён!", extra_tags="profile_update_success")
        return redirect(redirect_to)

    except ValidationError as e:
        # Обрабатываем ВСЕ ошибки валидации
        for field, errors in e.error_dict.items():
            for error in errors:
                if field == 'email':
                    messages.error(request, message="Этот email уже занят другим пользователем.", extra_tags="profile_update_error")
                elif field == 'phone':
                    messages.error(request, message="Этот телефон уже занят другим пользователем.", extra_tags="profile_update_error")
                else:
                    messages.error(request, message=f"Ошибка: {error.messages[0]}", extra_tags="profile_update_error")
        return redirect(redirect_to)

    except IntegrityError as e:
        # Обрабатываем ошибки уникальности из БД
        if 'email' in str(e):
            messages.error(request, message="Этот email уже занят", extra_tags="profile_update_error")
        if 'phone' in str(e):
            messages.error(request, message="Этот телефон уже занят", extra_tags="profile_update_error")
        
        return redirect(redirect_to)

    except Exception as e:
        messages.error(request, message=f"Неизвестная ошибка: {e}.", extra_tags="profile_update_error")
        
        return redirect(redirect_to)
