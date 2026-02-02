from decimal import Decimal

from django.db.models import Sum, Count, Value,Subquery,OuterRef, Avg
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.users.models import User
from apps.partnerships.models import ProjectPartner
from apps.tracking.models import Conversion
from apps.core.decorators import role_required

@role_required('advertiser')
def partners_json(request,partner_id):
    user = request.user 

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

    # Подзапрос для среднего количества
    conversion_avg_subquery = Conversion.objects.filter(
        partner__user_id=OuterRef('pk'),
        project__advertiser=user
    ).values('partner__user_id').annotate(
        avg=Avg('amount')
    ).values('avg')[:1]

    # Подзапрос для всех подключений
    all_connections_subquery = ProjectPartner.objects.filter(
        partner=OuterRef('pk'),
        advertiser=user,
    ).exclude(project__status='Удалено').values('partner').annotate(
        count=Count('id')
    ).values('count')[:1]

    # Подзапрос для активных подключений
    active_connections_subquery = ProjectPartner.objects.filter(
        partner=OuterRef('pk'),
        advertiser=user,
        status=ProjectPartner.StatusType.ACTIVE
    ).exclude(project__status='Удалено').values('partner').annotate(
        count=Count('id')
    ).values('count')[:1]

    # Подзапрос для приостановленных подключений
    paused_connections_subquery = ProjectPartner.objects.filter(
        partner=OuterRef('pk'),
        status=ProjectPartner.StatusType.SUSPENDED
    ).exclude(project__status='Удалено').values('partner').annotate(
        count=Count('id')
    ).values('count')[:1]

    partner = get_object_or_404(
        User.objects
        .select_related('partner_profile') 
        .prefetch_related(
            'project_memberships',
            'project_memberships__project'
        ).annotate(
            conversions_total=Coalesce(Subquery(conversion_sum_subquery), Value(Decimal('0'))),
            conversions_count=Coalesce(Subquery(conversion_count_subquery), Value(0)),
            conversions_avg=Coalesce(Subquery(conversion_avg_subquery), Value(Decimal('0'))),
            active_connections=Coalesce(Subquery(active_connections_subquery), Value(0)),
            paused_connections=Coalesce(Subquery(paused_connections_subquery), Value(0)),
            connections_count=Coalesce(Subquery(all_connections_subquery),Value(0))
        ),
        id=partner_id
    )
    if not hasattr(partner,'partner_profile'):
        return JsonResponse({"success":False,'details':"not partner"})
    
    return JsonResponse({
        "partner":{
            "username":partner.username,
            "total_income":partner.conversions_total,
            "conversions_count":partner.conversions_count,
            "average_conversion_rate": f"{partner.conversions_avg:.2f}",
            "projects": {
                "count":partner.connections_count,
                "active":partner.active_connections,
                "on_pause":partner.paused_connections
            }
            },
        "partnerships": [
            {
                "project_name":partnership.project.name,
                "partnership_status":partnership.status,
                "project_status":partnership.project.status,
                "project_description":partnership.project.description,
                "joined_at": partnership.joined_at,
                "cpa":partnership.project.cost_per_action,
                "income":partnership.project.get_partnership_conversions_sum(partner,partnership),
                "conversions_count": partnership.project.get_partnerhip_conversions_count(partner,partnership),
                "conversion_rate":partnership.project.get_partnerhip_conversion_percent(partner,partnership)
            } for partnership in partner.project_memberships.filter(advertiser=user).exclude(project__status='Удалено')
        ]
    })