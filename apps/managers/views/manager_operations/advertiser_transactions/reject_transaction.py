from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404

from apps.advertisers.models import AdvertiserTransaction,AdvertiserActivity
from apps.core.decorators import role_required
from utils import send_email_via_mailru


@role_required('manager')
@require_POST
@transaction.atomic
def reject_adv_transaction(request,transaction_id):
    """Отклонить заявку на пополнение рекламодателя"""
    
    transaction = get_object_or_404(
        AdvertiserTransaction.objects.select_related('advertiser__user'),
        id=transaction_id
    )

    if transaction.status == transaction.STATUS_CHOICES.COMPLETED:
        return JsonResponse({"success":False,"data":request.POST,'details':'Транзакция уже завершена'},status=403)
    rejection_reason = f"Причина: {request.POST.get('rejection_reason','')}"
    if not rejection_reason:
        rejection_reason = 'Причина не указана'
    msg =f"""Здравствуйте!

Благодарим вас за вашу заявку на пополнение баланса. К сожалению, мы вынуждены сообщить вам, что ваша заявка была отклонена.
{rejection_reason}
Если вы считаете, что это ошибка, пожалуйста, свяжитесь с нашей службой поддержки.
Приносим извинения за возможные неудобства и надеемся на ваше понимание.
Id транзакции: {transaction_id}
С уважением,  
Команда LinkOffer"""
    messages.success(request,message="Заявка на пополнение была отклонена!",extra_tags='adv_transaction_success')
    message_list = messages.get_messages(request)
    messages_data = [{"level": message.level_tag, "message": str(message)} for message in message_list]
    transaction.status = AdvertiserTransaction.STATUS_CHOICES.REJECTED
    transaction.rejection_reason = rejection_reason if not None else ""
    transaction.save()
    try:
        send_email_via_mailru.delay(transaction.advertiser.user.email, msg, "Заявка на пополнение баланса была отклонена!")
    except:
        pass
    AdvertiserActivity.objects.create(
        advertiser=transaction.advertiser,
        activity_type=AdvertiserActivity.ActivityType.REJECT,
        title='Пополнение баланса',
        details=f'Заявка на пополнение баланса была отклонена.{rejection_reason}'
    )
    return JsonResponse({"success":True,"data":request.POST,"messages":messages_data},status=200)
