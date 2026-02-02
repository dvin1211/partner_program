from django.shortcuts import render

from apps.core.decorators import role_required
from apps.managers.views.utils import get_manager_stats



@role_required('manager')
def settings(request):  
    """Настройки партнёра"""
    user = request.user
    
    context = {
        **get_manager_stats(user)
    }
    
    return render(request, 'managers/settings/settings.html',context=context)