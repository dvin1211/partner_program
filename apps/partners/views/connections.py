import json

from django.shortcuts import render

from apps.core.decorators import role_required
from apps.partners.models import PartnerActivity
from utils import _apply_search, _paginate
from .common import _get_connected_projects


@role_required('partner')
def connections(request):  
    """подключенные проекты"""
    user = request.user
    if not user.profile_completed:
        user.partner_profile.is_complete_profile()
    
    notifications_count = PartnerActivity.objects.filter(partner=request.user.partner_profile,is_read=False).count()
    
    connection_search_q = request.GET.get('connections_search', '').strip()
    partnerships = _get_connected_projects(request)
    for partnership in partnerships:
        partnership.project.conversions_count_value = partnership.project.get_partnerhip_conversions_count(user,partnership)
        partnership.project.clicks_count_value = partnership.project.get_partnerhip_clicks_count(user,partnership)
        partnership.project.conversions_percent_value = partnership.project.get_partnerhip_conversion_percent(user,partnership)
        partnership.project.has_link = partnership.project.has_partner_link(user)
        partnership.project.params_json = json.dumps(list(
            partnership.project.params.all().values('name', 'description', 'param_type', 'example_value')
        ))
    if connection_search_q:
        partnerships = _apply_search(partnerships, connection_search_q, ['name'])
    
    # Общая статистика
    total_connected_projects = partnerships.count()
    active_connected_projects = partnerships.filter(
        status="Активен"
    ).count()
    suspended_connected_projects = partnerships.filter(
        status="Приостановлен"
    ).count()
    
    partnerships_page = _paginate(request, partnerships, 5, 'connected_projects_page')

    context = {
        "user":user,
        'notifications_count':notifications_count,
        
        'partnerships': partnerships_page,
        'total_connected_projects':total_connected_projects,
        'active_connected_projects':active_connected_projects,
        'suspended_connected_projects':suspended_connected_projects
    }
    
    return render(request, 'partners/connections/connections.html',context=context)