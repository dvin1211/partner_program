from django.shortcuts import render
from django.db.models import Q

from apps.partners.models import PartnerTransaction
from apps.core.decorators import role_required
from apps.partners.models import PartnerTransaction
from apps.managers.views.utils import get_manager_stats
from utils import _paginate


@role_required('manager')
def manager_partners(request):  
    """Модерация выплат партнёрам"""
    user = request.user
    
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
    
    context = {
        "users_search_q":users_search_q,
        "transactions_type_q":transactions_type_q,
        "transactions":transactions_page,
        
        **get_manager_stats(user)
    }
    
    return render(request, 'managers/partners/partners.html',context=context)


