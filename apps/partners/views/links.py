from decimal import Decimal

from django.shortcuts import render
from django.db.models import Count, F, FloatField, ExpressionWrapper, Sum,Value, Prefetch
from django.db.models.functions import Coalesce

from apps.partners.models import PartnerActivity,PartnerLink
from apps.advertisers.models import ProjectParam
from apps.core.decorators import role_required
from utils import _paginate


@role_required('partner')
def links(request):  
    """сгенерированные ссылки партнёра"""
    user = request.user
    if not user.profile_completed:
        user.partner_profile.is_complete_profile()
    
    active_links = PartnerLink.objects.filter(
        partner=user,
        is_active=True
    ).count()
    
    clicks_count = user.partner_profile.clicks.count()
    
    if clicks_count == 0:
        conversion = 0
    else:
        conversion =  f"{(user.partner_profile.conversions.count() / user.partner_profile.clicks.count()) * 100:.2f}"
    
    notifications_count = PartnerActivity.objects.filter(partner=user.partner_profile,is_read=False).count()
    
    best_link = PartnerLink.objects.filter(partner=user).annotate(
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
        partner=user
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
        "user":user,
        'notifications_count':notifications_count,
        
        "clicks_count": clicks_count,
        "active_links":active_links,
        "conversion":conversion,
        "best_link":best_link,
        "partner_links":partner_links_page
    }
    
    return render(request, 'partners/links/links.html',context=context)