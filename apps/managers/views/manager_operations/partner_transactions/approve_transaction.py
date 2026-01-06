from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from apps.core.decorators import role_required
from apps.users.models import User
from apps.partners.models import PartnerTransaction, PartnerActivity
from utils import send_email_via_mailru


@role_required('manager')
@require_POST
def approve_transaction(request, transaction_id,partner_id):
    """Одобрить вывод средств партнёра"""
    transaction = get_object_or_404(PartnerTransaction,id=transaction_id)
    transaction.status = PartnerTransaction.STATUS_CHOICES.COMPLETED
    transaction.save()
    
    user = get_object_or_404(User,id=partner_id)
    PartnerActivity.objects.create(
        partner=user.partner_profile,
        activity_type=PartnerActivity.ActivityType.PAYOUT,
        title='Выплата средств одобрена',
        details=f'Модератор одобрил транзакцию №{transaction_id}.'
    )
    messages.success(request, message=f'Заявка #{transaction.id} на сумму {transaction.amount}₽ одобрена',extra_tags='approve_payout_success')
    try:
        send_email_via_mailru.delay(user.email,f"Модератор одобрил транзакцию №{transaction_id} на сумму {transaction.amount}","Одобрена выплата средств")
    except:
        pass
    return redirect('manager_partners')