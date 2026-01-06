from datetime import timedelta
import json 

from django.shortcuts import render
from django.db.models import Count, F, FloatField, ExpressionWrapper, Sum,Avg,Q,Value,OuterRef,Subquery
from django.db.models.functions import TruncDate,Coalesce
from django.utils import timezone

from apps.advertisers.models import Project
from apps.core.decorators import role_required
from apps.partners.models import PartnerActivity,Platform
from apps.tracking.models import Conversion,ClickEvent
from decimal import Decimal
from utils import _paginate


@role_required('partner')
def stats(request):
    """Статистика партнёра"""

    user = request.user
    if not user.profile_completed:
        user.partner_profile.is_complete_profile()
    
    conversions = Conversion.objects.filter(
        partner=user.partner_profile
        ).select_related(
            "project","platform"
            ).only(
                'id',
                'project',
                'platform',
                'created_at',
                'amount'
            ).order_by(
                "-created_at")
    conversions_count = conversions.count()
    conversions_page = _paginate(request,conversions,6,'conversions_page')

    clicks = ClickEvent.objects.filter(partner=user.partner_profile).order_by('-created_at') 
    clicks_count = clicks.count()

    last_30_days = timezone.now() - timedelta(days=30)
    conversions_by_day = Conversion.objects.filter(
        partner=user.partner_profile,
        created_at__gte=last_30_days
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    # Агрегируем клики по дням
    clicks_by_day = ClickEvent.objects.filter(
        partner=user.partner_profile,
        created_at__gte=last_30_days
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    # Создаем словари для быстрого доступа
    conversions_dict = {item['date']: item['count'] for item in conversions_by_day}
    clicks_dict = {item['date']: item['count'] for item in clicks_by_day}

    # Генерируем все даты за период
    all_dates = []
    current_date = last_30_days.date()
    while current_date <= timezone.now().date():
        all_dates.append(current_date)
        current_date += timedelta(days=1)

    # Формируем данные для Chart.js
    chart_data = {
        'labels': [date.strftime("%d-%m-%y") for date in all_dates],
        'datasets': [
            {
                'label': 'Конверсии',
                'data': [conversions_dict.get(date, 0) for date in all_dates],
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.1
            },
            {
                'label': 'Клики', 
                'data': [clicks_dict.get(date, 0) for date in all_dates],
                'borderColor': 'rgb(255, 99, 132)',
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'tension': 0.1
            }
        ]
    }

    
    last_month = timezone.now() - timedelta(days=30)

    total_revenue = Conversion.objects.filter(partner=user.partner_profile).aggregate(total=Coalesce(Sum('amount'),0.0,output_field=FloatField()))['total'] or 0
    total_revenue_last_month = Conversion.objects.filter(partner=user.partner_profile,created_at__gte=last_month).aggregate(total=Coalesce(Sum('amount'),0.0,output_field=FloatField()))['total'] or 0
    average_revenue = f"{Conversion.objects.filter(partner=user.partner_profile).aggregate(total=Coalesce(Avg('amount'),0.0, output_field=FloatField()))['total']:.2f}" or 0

    top_projects = Project.objects.filter(
        partner_memberships__partner=user,
        deleted_at__isnull = True,
        is_active=True
    ).annotate(
        total_amount=Coalesce(Sum(
            'conversions__amount',
            filter=Q(conversions__partner=user.partner_profile)
        ), Value(Decimal('0.00'))),
        conversion_count=Coalesce(Count(
            'conversions',
            filter=Q(conversions__partner=user.partner_profile)
        ), 0),
        score=ExpressionWrapper(
            F('conversion_count') * 0.5 + F('total_amount') * 0.3,
            output_field=FloatField()
        )
    ).order_by('-score')[:4]
    
    for project in top_projects:
        project.cr = project.get_partner_conversion_percent(user)

    conversion_sum_subquery = Conversion.objects.filter(
        platform=OuterRef('pk')
    ).values('platform').annotate(
        total=Sum('amount')
    ).values('total')[:1]

    click_count_subquery = ClickEvent.objects.filter(
        platform=OuterRef('pk')
    ).values('platform').annotate(
        cnt=Count('id')
    ).values('cnt')[:1]

    conversion_count_subquery = Conversion.objects.filter(
        platform=OuterRef('pk')
    ).values('platform').annotate(
        cnt=Count('id')
    ).values('cnt')[:1]

    top_platforms = Platform.objects.filter(
        partner=user,
        deleted_at__isnull = True,
        is_active=True
    ).annotate(
        total_revenue=Coalesce(Subquery(conversion_sum_subquery), Value(Decimal('0.00'))),
        click_count=Coalesce(Subquery(click_count_subquery), Value(0)),
        conversion_count=Coalesce(Subquery(conversion_count_subquery), Value(0)),
        score=ExpressionWrapper(
            F('conversion_count') * 0.5 + F('click_count') * 0.3,
            output_field=FloatField()
        )
    ).order_by('-score')[:4]

    notifications_count = PartnerActivity.objects.filter(partner=user.partner_profile,is_read=False).count()
    
    context = {
        "user":user,
        'notifications_count':notifications_count,

        "conversions":conversions_page,
        "conversions_count":conversions_count,

        "clicks":clicks,
        "clicks_count":clicks_count,

        "total_revenue":total_revenue,
        "total_revenue_last_month":total_revenue_last_month,
        "average_revenue": average_revenue,

        "top_projects": top_projects,
        "top_platforms": top_platforms,

        "conversions_json": json.dumps(chart_data) if chart_data else None,
    }
    
    return render(request, 'partners/stats/stats.html',context=context)