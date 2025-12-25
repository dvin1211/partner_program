from decimal import Decimal
from datetime import timedelta

from django.shortcuts import render
from django.db.models import Count, Sum,Value,Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.core.decorators import role_required
from apps.partners.forms import PlatformForm
from apps.partners.models import PartnerActivity, Platform
from utils import _paginate, _apply_search


@role_required('partner')
def platforms(request):  
    """Площадки партнёра"""
    user = request.user
    user.partner_profile.is_complete_profile()
    
    notifications_count = PartnerActivity.objects.filter(partner=user.partner_profile,is_read=False).count()
    
    platforms_search_q = request.GET.get('platforms_search', '').strip()
    
    three_days_ago = timezone.now() - timedelta(days=3)
    platforms = Platform.objects.filter(
        Q(deleted_at__isnull=True) | Q(deleted_at__isnull=False,deleted_at__gte=three_days_ago),
        partner=user,
    ).annotate(
        conversions_total=Coalesce(Sum('conversions__amount'), Value(Decimal(0.0))),
        conversion_count=Coalesce(Count('conversions'),Value(0))
    ).order_by('-created_at')
    
    total_platforms = platforms.count()
    approved_platforms = platforms.filter(status='Подтверждено').count()
    pending_platforms = platforms.filter(status='На модерации').count()
    rejected_platforms = platforms.filter(status='Отклонено').count()
    
    if platforms_search_q:
        platforms = _apply_search(platforms, platforms_search_q, ['name'])
        
    platform_page = _paginate(request, platforms, 5, 'platforms_page')
    
    context = {
        'notifications_count':notifications_count,
        
        'platformForm': PlatformForm(),
        
        "platforms":platform_page,
        
        "total_platforms": total_platforms,
        "approved_platforms_count": approved_platforms,
        "pending_platforms_count":pending_platforms,
        "rejected_platforms_count":rejected_platforms,
        
        "platforms_search_query": platforms_search_q,
    }
    
    return render(request, 'partners/platforms/platforms.html',context=context)