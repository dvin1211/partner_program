from django.shortcuts import render,redirect
from django.db.models import Q

from apps.partners.models import Platform
from apps.managers.models import ManagerActivity
from utils import _paginate

def manager_platforms(request):  
    """Модерация проектов"""
    user = request.user
    if not user.is_authenticated:
        return redirect('/?show_modal=auth')
    if not hasattr(request.user,"managerprofile"):
        return redirect('index')
    if user.is_authenticated and user.is_currently_blocked():
        return render(request, 'account_blocked/block_info.html')
    
    platforms_search_q = request.GET.get('platforms_search','').strip()
    
    count = 10
    
    platforms = Platform.objects.filter(status='На модерации')
    
    if platforms_search_q:
        platforms = platforms.filter(
            Q(name__icontains=platforms_search_q) 
        )
    
    platforms = _paginate(request, platforms, count, "platforms_page")

    notifications_count = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False).count()
    
    context = {
        "user": request.user,  
        "platforms":platforms,
        "notifications_count":notifications_count,
        
        "platforms_search_q":platforms_search_q
    }
    
    return render(request, 'managers/platforms/platforms.html',context=context)


