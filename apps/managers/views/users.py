from django.shortcuts import render
from django.db.models import Q

from apps.core.decorators import role_required
from apps.users.models import User
from apps.managers.views.utils import get_manager_stats
from utils import _paginate


@role_required('manager')
def manager_users(request):  
    """Модерация пользователей"""
    user = request.user
    
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
    
    context = {
        "user": user,
        
        **get_manager_stats(user),

        "users":users,
        "users_type_q":users_type_q,
        "users_search_q":users_search_q,
        
    }
    
    return render(request, 'managers/users/users.html',context=context)


