from decimal import Decimal

from django.db.models import Prefetch, Value, Sum, Q,Subquery,OuterRef
from django.db.models.functions import Coalesce

from apps.advertisers.models import Project
from apps.partnerships.models import ProjectPartner
from apps.tracking.models import Conversion

def _get_available_projects(request):
    """Получение доступных проектов с оптимизацией"""
    return Project.objects.filter(
        status=Project.StatusType.APPROVED,
        is_active=True
    ).exclude(
        partners=request.user 
    ).select_related(
        'advertiser' 
    ).order_by('-created_at')
    
    
def _get_connected_projects(request):
    """Получение подключенных проектов у партнёра"""
    user_memberships_prefetch = Prefetch(
        'partner_memberships',
        queryset=ProjectPartner.objects.filter(partner=request.user),
        to_attr='user_memberships'
    )
    
    return Project.objects.filter(
        partner_memberships__partner=request.user
    ).prefetch_related(
        'params',
        user_memberships_prefetch,
        'project_links',
        'conversions'
    ).annotate( 
        conversions_total=Coalesce(Sum(
            'conversions__amount',
            filter=Q(conversions__partner=request.user.partner_profile)
        ),Value(Decimal('0.00')))
    ).order_by('-partner_memberships__joined_at')