from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.utils import IntegrityError
from django.views.decorators.http import require_POST

from apps.users.forms import PartnerRegistrationForm, AdvertiserRegistrationForm
from apps.partners.models import PartnerPayoutSettings

@require_POST
def handle_registration(request):
    """Обработчик регистрации"""
    user_type = request.POST.get('reg_type')
    form_class = PartnerRegistrationForm if user_type == "partner" else AdvertiserRegistrationForm
    form = form_class(request.POST or None)
    
    if not form.is_valid():
        process_form_errors(request, form, user_type)
        return redirect(f'/?show_modal={user_type}')
    
    try:
        user = form.save()
        if user_type == "partner":
            payout_settings = PartnerPayoutSettings.objects.create(
                partner=user
            )

            payout_settings.save()


        authenticated_user = authenticate(
            request, 
            email=user.email, 
            password=form.cleaned_data.get('password1')
        )
        
        if authenticated_user:
            login(request, authenticated_user)
            return redirect('dashboard')
            
        messages.error(
            request, 
            "Ошибка автоматической авторизации. Пожалуйста, войдите вручную.",
            extra_tags=f"reg_error_{user_type}"
        )
        
    except IntegrityError:
        messages.error(
            request,
            "Пользователь с таким email или логином уже существует",
            extra_tags=f"reg_error_{user_type}"
        )
    except Exception as e:
        messages.error(
            request,
            f"Произошла ошибка при регистрации: {str(e)}",
            extra_tags=f"reg_error_{user_type}"
        )
    
    return redirect(f'/?show_modal={user_type}')


def process_form_errors(request, form, user_type):
    """Обработка ошибок формы"""
    error_messages = {
        ('email', 'already exists'): "Пользователь с таким email уже зарегистрирован",
        ('password1', 'too short'): "Пароль должен содержать минимум 8 символов",
        ('password1', 'too common'): "Пароль слишком простой",
        ('password2', 'mismatch'): "Пароли не совпадают",
    }
    
    for field, errors in form.errors.items():
        for error in errors:
            error_lower = error.lower()
            message = None
            
            # Ищем кастомное сообщение
            for (field_key, error_key), msg in error_messages.items():
                if field == field_key and error_key in error_lower:
                    message = msg
                    break
            
            # Если не нашли кастомное, используем стандартное
            if not message:
                message = error
                
            messages.error(request, message, extra_tags=f"reg_error_{user_type}")