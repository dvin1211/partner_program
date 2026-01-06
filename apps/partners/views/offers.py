from django.contrib import messages
from django.shortcuts import render

from apps.core.decorators import role_required
from apps.partners.models import PartnerActivity
from utils import _paginate
from .common import _get_available_projects


@role_required("partner")
def offers(request):  
    """Доступные предложения"""
    user = request.user
    if not user.profile_completed:
        user.partner_profile.is_complete_profile()
        
    projects_search_q = ''
    
    notifications_count = PartnerActivity.objects.filter(partner=user.partner_profile,is_read=False).count()
         
    

    is_completed_profile = user.partner_profile.is_complete_profile()
    if not is_completed_profile:
        available_projects_page = []
        for i in range(0,6):
            project = {
                "name":"test_project"+str(i),
                "cost_per_action":-1,
                "advertiser": "Иван Иванов",
                "partners":{
                    "count": 0
                },
                "created_at":"2025-10-06 17:23:47.494 +0300"

            }
            available_projects_page.append(project)
        total_projects = 6
    else:
        projects_search_q = request.GET.get('offers_search', '').strip()
        available_projects = _get_available_projects(request)
        total_projects = available_projects.count()
        available_projects_page = _paginate(request, available_projects, 6, 'projects_page')

    context = {
        "notifications_count":notifications_count,

        "offers_search_query": projects_search_q,
        "total_projects":total_projects,
        'projects': available_projects_page,
        
    }
    
    return render(request, 'partners/offers/offers.html',context=context)