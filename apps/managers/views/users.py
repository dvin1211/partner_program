from django.shortcuts import render,redirect
from django.db.models import Q

from apps.users.models import User
from apps.managers.models import ManagerActivity
from utils import _paginate


def manager_users(request):  
    """Модерация пользователей"""
    user = request.user
    if not user.is_authenticated:
        return redirect('/?show_modal=auth')
    if not hasattr(request.user,"managerprofile"):
        return redirect('index')
    if user.is_authenticated and user.is_currently_blocked():
        return render(request, 'account_blocked/block_info.html')
    
    users_search_q = request.GET.get('users_search','').strip()
    users_type_q = request.GET.get('users_type','').strip()
    
    users = User.objects.filter(user_type__in=['partner', 'advertiser']).order_by("-date_joined")
    count = 10
    
    if users_search_q:
        users = users.filter(
            Q(username__icontains=users_search_q) |
            Q(first_name__icontains=users_search_q) |
            Q(last_name__icontains=users_search_q) |
            Q(email__icontains=users_search_q) | 
            Q(phone__icontains=users_search_q) 
        )
    
    if users_type_q and users_type_q != 'all':
        users = users.filter(user_type=users_type_q)
    
    users = _paginate(request,users,count,"users_page")

    notifications_count = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False).count()
    
    context = {
        "user": request.user,
        
        "notifications_count":notifications_count,

        "users":users,
        "users_type_q":users_type_q,
        "users_search_q":users_search_q,
        
    }
    
    return render(request, 'managers/users/users.html',context=context)


