from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.conf import settings 

from apps.advertisers.models import AdvertiserTransaction,AdvertiserActivity
from apps.core.decorators import role_required
from utils import send_email_via_mailru


@role_required('manager')
@require_POST
@transaction.atomic
def approve_adv_transaction(request, transaction_id):
    """Одобрить заявку на пополнение рекламодателя"""
    
    transaction = get_object_or_404(
        AdvertiserTransaction.objects.select_related('advertiser'),
        id=transaction_id
    )
    
    if transaction.status == transaction.STATUS_CHOICES.COMPLETED:
        return JsonResponse({
            "success": False,
            "error": "Транзакция уже завершена"
        }, status=403)
    
    # Рассчитываем сумму
    fee_percent = Decimal(str(settings.PARTNER_PAYOUT_SETTINGS["fee_percent"]))
    amount = transaction.amount - ((transaction.amount / 100) * fee_percent)
    
    # Сообщение пользователю
    messages.success(
        request,
        "Заявка на пополнение была одобрена!",
        extra_tags='adv_transaction_success'
    )
    
    # Обновляем транзакцию и баланс
    transaction.status = AdvertiserTransaction.STATUS_CHOICES.COMPLETED
    transaction.save()
    
    transaction.advertiser.balance += amount
    transaction.advertiser.save()
    
    # Email через on_commit
    def send_approval_email():
        try:
            msg = f"""Здравствуйте!
Мы рады сообщить вам, что ваш баланс был успешно пополнен на сумму {amount}₽ с учётом комиссии {fee_percent}%. 
Спасибо, что остаетесь с нами! Если у вас есть вопросы или нужна помощь, не стесняйтесь обращаться в нашу службу поддержки.
Id транзакции: {transaction_id}
С уважением,  
Команда LinkOffer"""
            
            send_email_via_mailru.delay(
                transaction.advertiser.user.email,
                msg,
                "Ваш баланс был пополнен!"
            )
        except Exception as e:
            pass
    
    transaction.on_commit(send_approval_email)
    
    # Логируем активность
    AdvertiserActivity.objects.create(
        advertiser=transaction.advertiser,
        activity_type=AdvertiserActivity.ActivityType.TOPUP,
        title='Пополнение баланса',
        details=f'Ваш баланс был пополнен на сумму: {amount}₽ с учётом комиссии {fee_percent}%.'
    )
    
    # Подготавливаем ответ
    message_list = messages.get_messages(request)
    messages_data = [
        {"level": message.level_tag, "message": str(message)}
        for message in message_list
    ]
    
    return JsonResponse({
        "success": True,
        "transaction_id": transaction_id,
        "net_amount": str(amount),
        "status": "completed",
        "messages": messages_data
    }, status=200)