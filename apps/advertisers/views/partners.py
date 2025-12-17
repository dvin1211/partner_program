from decimal import Decimal

from django.shortcuts import render, redirect
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count, Value,Subquery,OuterRef

from apps.users.models import User
from apps.advertisers.models import AdvertiserActivity
from apps.tracking.models import Conversion
from utils import _paginate,_apply_search

def partners(request):
    """Страница с подключенными партнёрами рекламодателя"""
    user = request.user
    if not user.is_authenticated:
        return redirect('/?show_modal=auth')
    if not hasattr(request.user,"advertiserprofile"):
        return redirect('index')
    if user.is_authenticated and user.is_currently_blocked():
        return render(request, 'account_blocked/block_info.html')
    
    notifications_count = AdvertiserActivity.objects.filter(advertiser=request.user.advertiserprofile,is_read=False).count()
    
    conversion_sum_subquery = Conversion.objects.filter(
        partner__user_id=OuterRef('pk'),
        project__advertiser=request.user
    ).values('partner__user_id').annotate(
        total=Sum('amount')
    ).values('total')[:1]

    # Подзапрос для количества
    conversion_count_subquery = Conversion.objects.filter(
        partner__user_id=OuterRef('pk'),
        project__advertiser=request.user
    ).values('partner__user_id').annotate(
        count=Count('id')
    ).values('count')[:1]

    partners = User.objects.filter(
        project_memberships__project__advertiser=request.user
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