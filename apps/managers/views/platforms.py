from django.shortcuts import render
from django.db.models import Q

from apps.partners.models import Platform
from apps.core.decorators import role_required
from apps.partners.models import Platform
from apps.managers.views.utils import get_manager_stats
from utils import _paginate


@role_required('manager')
def manager_platforms(request):  
    """Модерация проектов"""
    user = request.user
    
    platforms_search_q = request.GET.get('platforms_search','').strip()
    
    count = 10
    
    platforms = Platform.objects.filter(status='На модерации')
    
    if platforms_search_q:
        platforms = platforms.filter(
            Q(name__icontains=platforms_search_q) 
        )
    
    platforms = _paginate(request, platforms, count, "platforms_page")

    context = {
        "user": user,  
        "platforms":platforms,

        **get_manager_stats(user),
        
        "platforms_search_q":platforms_search_q
    }
    
    return render(request, 'managers/platforms/platforms.html',context=context)


