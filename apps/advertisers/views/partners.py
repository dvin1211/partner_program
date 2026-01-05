from decimal import Decimal

from django.shortcuts import render
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count, Value,Subquery,OuterRef

from apps.advertisers.models import AdvertiserActivity
from apps.core.decorators import role_required
from apps.tracking.models import Conversion
from apps.users.models import User
from utils import _paginate,_apply_search


@role_required('advertiser')
def partners(request):
    """Страница с подключенными партнёрами рекламодателя"""
    user = request.user
    user.advertiserprofile.is_complete_profile()
    
    notifications_count = AdvertiserActivity.objects.filter(advertiser=user.advertiserprofile,is_read=False).count()
    
    # Подзапрос для суммы конверсий
    conversion_sum_subquery = Conversion.objects.filter(
        partner__user_id=OuterRef('pk'),
        project__advertiser=user
    ).values('partner__user_id').annotate(
        total=Sum('amount')
    ).values('total')[:1]

    # Подзапрос для количества
    conversion_count_subquery = Conversion.objects.filter(
        partner__user_id=OuterRef('pk'),
        project__advertiser=user
    ).values('partner__user_id').annotate(
        count=Count('id')
    ).values('count')[:1]

    partners = User.objects.filter(
        project_memberships__project__advertiser=user
    ).annotate(
        conversions_total=Coalesce(Subquery(conversion_sum_subquery), Value(Decimal(0))),
        conversions_count=Coalesce(Subquery(conversion_count_subquery), Value(0))
    ).order_by("-date_joined").distinct()

    partners_search_q = request.GET.get('partners_search', '').strip()
    
    if partners_search_q:
        partners = _apply_search(partners,partners_search_q,["username"])
    
    partners_page = _paginate(request, partners, 6, 'partners_page')
    
    context = {
        "notifications_count":notifications_count,
        
        "partners":partners_page,
        'partners_search_query':partners_search_q,
    }
    return render(request, 'advertisers/partners/partners.html',context=context)