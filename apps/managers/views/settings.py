from django.shortcuts import render

from apps.core.decorators import role_required
from apps.managers.models import ManagerActivity


@role_required('manager')
def settings(request):  
    """Настройки партнёра"""
    user = request.user
    
    notifications_count = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False).count()

    context = {
        "notifications_count":notifications_count
    }
    
    return render(request, 'managers/settings/settings.html',context=context)