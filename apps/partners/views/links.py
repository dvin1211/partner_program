from decimal import Decimal

from django.shortcuts import render,redirect
from django.db.models import Count, F, FloatField, ExpressionWrapper, Sum,Value, Prefetch
from django.db.models.functions import Coalesce

from apps.partners.models import PartnerActivity,PartnerLink
from apps.advertisers.models import ProjectParam
from utils import _paginate

def links(request):  
    """сгенерированные ссылки партнёра"""
    user = request.user
    if not user.is_authenticated:
        return redirect('/?show_modal=auth')
    if not hasattr(request.user,"partner_profile"):
        return redirect('index')
    if user.is_authenticated and user.is_currently_blocked():
        return render(request, 'account_blocked/block_info.html')
    
    active_links = PartnerLink.objects.filter(
        partner=request.user,
        is_active=True
    ).count()
    
    clicks_count = request.user.partner_profile.clicks.count()
    
    if clicks_count == 0:
        conversion = 0
    else:
        conversion =  f"{(request.user.partner_profile.conversions.count() / request.user.partner_profile.clicks.count()) * 100:.2f}"
    
    notifications_count = PartnerActivity.objects.filter(partner=request.user.partner_profile,is_read=False).count()
    
    best_link = PartnerLink.objects.filter(partner=request.user).annotate(
        clicks_count=Count('clicks',distinct=True),
        conversions_count=Count('conversions',distinct=True),
            score=ExpressionWrapper(
                F('conversions_count') * 0.5 + F('clicks_count') * 0.3,
                output_field=FloatField()
            )
        ).filter(
            is_active=True
    ).order_by('-score').first()

    partner_links = PartnerLink.objects.filter(
        partner=request.user
    ).annotate(
        conversions_total=Coalesce(Sum('conversions__amount'), Value(Decimal(0.0)))
    ).select_related('project').prefetch_related(
        Prefetch(
            'project__params',
            queryset=ProjectParam.objects.all(),
            to_attr='project_params_list'
        )
    ).order_by('-created_at')
    for link in partner_links:
        link.params = [param.name for param in link.project.project_params_list if param.name != 'pid' and param.param_type == 'required']
    partner_links_page = _paginate(request, partner_links, 6, 'partner_links_page')
    context = {
        'notifications_count':notifications_count,
        
        "clicks_count": clicks_count,
        "active_links":active_links,
        "conversion":conversion,
        "best_link":best_link,
        "partner_links":partner_links_page
    }
    
    return render(request, 'partners/links/links.html',context=context)