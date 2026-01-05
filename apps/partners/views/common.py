from decimal import Decimal

from django.db.models import Value, Sum, Count, DecimalField, IntegerField,Subquery, OuterRef
from django.db.models.functions import Coalesce

from apps.advertisers.models import Project
from apps.partnerships.models import ProjectPartner
from apps.tracking.models import Conversion, ClickEvent

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
    """Получение подключенных проектов через модель ProjectPartner"""
    if not hasattr(request.user, 'partner_profile'):
        return []
    
    conversion_amount_subquery = Conversion.objects.filter(
            partnership=OuterRef('pk')
        ).values('partnership').annotate(
            total=Sum('amount')
        ).values('total')[:1]


    conversion_count_subquery = Conversion.objects.filter(
            partnership=OuterRef('pk')
        ).values('partnership').annotate(
            count=Count('id')
        ).values('count')[:1]
    
    clicks_count_subquery = ClickEvent.objects.filter(
            partnership=OuterRef('pk')
        ).values('partnership').annotate(
            total=Count('id')
        ).values('total')[:1]

    return ProjectPartner.objects.filter(
        partner=request.user).select_related(
         'partner'
    ).annotate(
        conversions_total=Coalesce(
            Subquery(conversion_amount_subquery),
            Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        conversions_count=Coalesce(
            Subquery(conversion_count_subquery),
            Value(0),
            output_field=IntegerField()
        ),
        clicks_count=Coalesce(
            Subquery(clicks_count_subquery),
            Value(0),
            output_field=IntegerField()
        )
    ).order_by('-joined_at')