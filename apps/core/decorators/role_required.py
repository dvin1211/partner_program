from functools import wraps 
from typing import Literal

from django.shortcuts import render,redirect


def role_required(role: Literal['partner','manager','advertiser']):
    """Функция для проверки типа пользователя

    Args:
        role (str): тип пользователя (Менеджер, рекламодатель, партнёр)
    """
    if role not in ('partner','manager','advertiser'):
        raise ValueError("Неверный тип пользователя")
    
    def check_perms(view_func):
        @wraps(view_func)
        def wrapper(request,*args,**kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('/?show_modal=auth')
            if user.user_type != role:
                return redirect('index')
            if user.is_currently_blocked():
                return render(request, 'account_blocked/block_info.html')
            return view_func(request,*args,**kwargs)
        return wrapper
    return check_perms