import json 

from django.shortcuts import render
from django.db.models import Sum, Avg

from apps.core.decorators import role_required
from apps.advertisers.models import AdvertiserActivity
from apps.tracking.models import Conversion
from utils import _paginate


@role_required('advertiser')
def sales(request):
    """Страница со статистикой о продажах рекламодателя"""
    
    user = request.user
    
    conversions = Conversion.objects.filter(project__advertiser=user).select_related("project","partner").order_by("-created_at")
    conversions_count = conversions.count()
    notifications_count = AdvertiserActivity.objects.filter(advertiser=user.advertiserprofile,is_read=False).count()
    
    
    chart_data = None
    if conversions:
        chart_data = [
        {
            "id": conv.id,
            "project": conv.project.name if conv.project else None, 
            "date": conv.created_at.strftime("%d-%m-%y"),  
            "amount": float(conv.amount) 
        }
        for conv in conversions
    ]
        conversions_average = f"{conversions.aggregate(avg_price=Avg('amount'))["avg_price"]:.2f}"
        conversions_total = f"{conversions.aggregate(total_price=Sum('amount'))["total_price"]:.2f}"
    else:
        conversions_total = 0
        conversions_average = 0
    
    conversions_page = _paginate(request,conversions,6,'conversions_page')
    
    context = {
        "notifications_count":notifications_count,
        
        "conversions":conversions_page,
        "conversions_count":conversions_count,
        "conversions_average":conversions_average,
        "conversions_total":conversions_total,
        "conversions_json": json.dumps(chart_data) if chart_data else None,
        
    }
    return render(request, 'advertisers/sales/sales.html',context=context)