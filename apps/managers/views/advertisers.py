from django.shortcuts import render,redirect
from django.db.models import Q

from utils import _paginate
from apps.advertisers.models import AdvertiserTransaction
from apps.managers.models import ManagerActivity

def manager_advertisers(request):  
    """Модерация пополнений баланса у рекламодателей"""
    user = request.user
    if not user.is_authenticated:
        return redirect('/?show_modal=auth')
    if not hasattr(request.user,"managerprofile"):
        return redirect('index')
    if user.is_authenticated and user.is_currently_blocked():
        return render(request, 'account_blocked/block_info.html')
    
    count = 10
    
    users_search_q = request.GET.get('users_search','').strip()
    transactions_type_q = request.GET.get('transactions_type_q','').strip()

    advertiser_transactions = AdvertiserTransaction.objects.order_by('-date')

    if users_search_q:
        advertiser_transactions = advertiser_transactions.filter(
            Q(advertiser__user__username__icontains=users_search_q) |
            Q(advertiser__user__first_name__icontains=users_search_q) |
            Q(advertiser__user__last_name__icontains=users_search_q) |
            Q(advertiser__user__email__icontains=users_search_q) | 
            Q(advertiser__user__phone__icontains=users_search_q) 
        )
    
    if transactions_type_q and transactions_type_q != 'all':
        advertiser_transactions = advertiser_transactions.filter(status=transactions_type_q)
    transactions = _paginate(request,advertiser_transactions,count,"transactions_page")

    notifications_count = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False).count()
    
    context = {
        "transactions_type_q":transactions_type_q,
        "users_search_q":users_search_q,
        "transactions": transactions,
        "notifications_count":notifications_count
    }
    
    return render(request, 'managers/advertisers/advertisers.html',context=context)


