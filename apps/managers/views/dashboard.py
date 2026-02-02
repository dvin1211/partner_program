from django.shortcuts import render

from apps.core.decorators import role_required
from apps.managers.models import ManagerActivity
from apps.managers.views.utils import get_manager_stats


@role_required('manager')
def manager_dashboard(request):  
    """Информационная панель менеджера"""
    user = request.user
    

    notifications = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False)
    
    context = {
        "user": user,  
        "notifications":notifications,

        **get_manager_stats(user)

    }
    
    return render(request, 'managers/dashboard/dashboard.html',context=context)


