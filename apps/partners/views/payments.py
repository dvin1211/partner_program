from django.conf import settings
from django.shortcuts import render
from django.db.models import Sum

from apps.core.decorators import role_required
from apps.partners.models import PartnerActivity, PartnerTransaction
from utils import _paginate


@role_required('partner')
def payments(request):  
    """Транзакции партнёра"""
    user = request.user
    if not user.profile_completed:
        user.partner_profile.is_complete_profile()

    notifications_count = PartnerActivity.objects.filter(partner=user.partner_profile,is_read=False).count()
    
    total_proccessing_payments = PartnerTransaction.objects.filter(
        status=PartnerTransaction.STATUS_CHOICES.PENDING
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_paid = PartnerTransaction.objects.filter(
        status=PartnerTransaction.STATUS_CHOICES.COMPLETED
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    transactions = PartnerTransaction.objects.filter(partner=user).order_by('-date')
    transactions_page = _paginate(request,transactions,5,'transactions_page')
    context = {
        "notifications_count":notifications_count,
        
        "total_proccessing_payments":total_proccessing_payments,
        "total_paid":total_paid,
        
        "transactions_page": transactions_page,
        
        "is_payout_available": user.partner_profile.balance > float(settings.PARTNER_PAYOUT_SETTINGS["min_amount"]),
        "min_payout": settings.PARTNER_PAYOUT_SETTINGS["min_amount"],
        "fee_percent": settings.PARTNER_PAYOUT_SETTINGS["fee_percent"],
    }
    
    return render(request, 'partners/payments/payments.html',context=context)