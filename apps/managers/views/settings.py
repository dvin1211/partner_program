from django.shortcuts import render,redirect

from apps.managers.models import ManagerActivity

def settings(request):  
    """Настройки партнёра"""
    user = request.user
    if not user.is_authenticated:
        return redirect('/?show_modal=auth')
    if not hasattr(request.user,"managerprofile"):
        return redirect('index')
    if user.is_authenticated and user.is_currently_blocked():
        return render(request, 'account_blocked/block_info.html')
    
    notifications_count = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False).count()

    context = {
        "notifications_count":notifications_count
    }
    
    return render(request, 'managers/settings/settings.html',context=context)