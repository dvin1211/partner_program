from django.shortcuts import render
from django.db.models import Q

from apps.core.decorators import role_required
from apps.advertisers.models import Project, AdvertiserTransaction
from apps.managers.models import ManagerActivity
from apps.partners.models import Platform,PartnerTransaction


@role_required('manager')
def manager_dashboard(request):  
    """Информационная панель менеджера"""
    user = request.user
    
    pending_projects_count = Project.objects.filter(status='На модерации').count()
    pending_platforms_count = Platform.objects.filter(status='На модерации').count()
    transactions_count = PartnerTransaction.objects.filter(status='В обработке').count()
    advertiser_transactions_count = AdvertiserTransaction.objects.filter(Q(status='В обработке') | Q(status='Обработано')).count()

    notifications = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False)
    notifications_count = notifications.count()
    
    context = {
        "user": user,  
        "pending_projects_count":pending_projects_count,
        "pending_platforms_count":pending_platforms_count,
        "transactions_count":transactions_count,
        "advertiser_transactions_count":advertiser_transactions_count,
        "notifications":notifications,
        "notifications_count":notifications_count
    }
    
    return render(request, 'managers/dashboard/dashboard.html',context=context)


