from django.shortcuts import render,redirect
from django.db.models import Q

from apps.advertisers.models import Project, AdvertiserTransaction
from apps.managers.models import ManagerActivity
from apps.partners.models import Platform,PartnerTransaction


def manager_dashboard(request):  
    """Информационная панель менеджера"""
    user = request.user
    if not user.is_authenticated:
        return redirect('/?show_modal=auth')
    if not hasattr(request.user,"managerprofile"):
        return redirect('index')
    if user.is_authenticated and user.is_currently_blocked():
        return render(request, 'account_blocked/block_info.html')
    
    pending_projects_count = Project.objects.filter(status='На модерации').count()
    pending_platforms_count = Platform.objects.filter(status='На модерации').count()
    transactions_count = PartnerTransaction.objects.filter(status='В обработке').count()
    advertiser_transactions_count = AdvertiserTransaction.objects.filter(Q(status='В обработке') | Q(status='Обработано')).count()

    notifications = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False)
    notifications_count = notifications.count()
    
    context = {
        "user": request.user,  
        "pending_projects_count":pending_projects_count,
        "pending_platforms_count":pending_platforms_count,
        "transactions_count":transactions_count,
        "advertiser_transactions_count":advertiser_transactions_count,
        "notifications":notifications,
        "notifications_count":notifications_count
    }
    
    return render(request, 'managers/dashboard/dashboard.html',context=context)


