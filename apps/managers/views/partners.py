from django.shortcuts import render,redirect
from django.db.models import Q

from utils import _paginate
from apps.partners.models import PartnerTransaction
from apps.managers.models import ManagerActivity

def manager_partners(request):  
    """Модерация выплат партнёрам"""
    user = request.user
    if not user.is_authenticated:
        return redirect('/?show_modal=auth')
    if not hasattr(user,"managerprofile"):
        return redirect('index')
    if user.is_authenticated and user.is_currently_blocked():
        return render(request, 'account_blocked/block_info.html')
    
    count = 10
    
    users_search_q = request.GET.get('users_search','').strip()
    transactions_type_q = request.GET.get('transactions_type_q','').strip()

    transactions = PartnerTransaction.objects.order_by('-date')
    if users_search_q:
        transactions = transactions.filter(
            Q(partner__username__icontains=users_search_q) |
            Q(partner__first_name__icontains=users_search_q) |
            Q(partner__last_name__icontains=users_search_q) |
            Q(partner__email__icontains=users_search_q) | 
            Q(partner__phone__icontains=users_search_q) 
        )
    if transactions_type_q and transactions_type_q != 'all':
        transactions = transactions.filter(status=transactions_type_q)
    transactions_page=_paginate(request,transactions,count,"transactions_page")
    
    notifications_count = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False).count()

    context = {
        "users_search_q":users_search_q,
        "transactions_type_q":transactions_type_q,
        "transactions":transactions_page,
        "notifications_count":notifications_count,
    }
    
    return render(request, 'managers/partners/partners.html',context=context)


