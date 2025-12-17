from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.conf import settings 

from apps.advertisers.models import AdvertiserTransaction,AdvertiserActivity
from utils import send_email_via_mailru,send_email_via_mailru_with_attachment

@require_POST
def proccess_adv_transaction(request,transaction_id):
    """Отправки реквизиты для заявки на пополнение рекламодателя"""
    transaction = get_object_or_404(AdvertiserTransaction,id=transaction_id)
    msg = """Здравствуйте
    
Мы рады сообщить вам, что ваш запрос на пополнение баланса был успешно обработан.
Реквизиты для перевода прикреплены в файле. Пожалуйста, используйте их для завершения оплаты.

Если у вас возникли вопросы или вам нужна помощь, не стесняйтесь обращаться в нашу службу поддержки.

С уважением,
Команда LinkOffer"""
    attachments = []
    if 'invoiceFile' in request.FILES:
        uploaded_file = request.FILES['invoiceFile']
        
        file_data = {
            'filename': str(uploaded_file.name),
            'content': uploaded_file.read(),
            'content_type': str(uploaded_file.content_type),
        }
        attachments.append(file_data)
    try:
        send_email_via_mailru_with_attachment(transaction.advertiser.user.email,msg,"Счет на оплату для пополнения баланса на вашем аккаунте",attachments)
    except:
        pass
    messages.success(request,message="Реквизиты для пополнения отправлены рекламодателю!",extra_tags='adv_transaction_success')
    message_list = messages.get_messages(request)
    messages_data = [{"level": message.level_tag, "message": str(message)} for message in message_list]
    transaction.status = AdvertiserTransaction.STATUS_CHOICES.PROCCESSED
    transaction.save()
    return JsonResponse({"success":True,"data":request.POST,"messages":messages_data},status=200)


@require_POST
def reject_adv_transaction(request,transaction_id):
    """Отклонить заявку на пополнение рекламодателя"""
    transaction = get_object_or_404(AdvertiserTransaction,id=transaction_id)
    if transaction.status == transaction.STATUS_CHOICES.COMPLETED:
        return JsonResponse({"success":False,"data":request.POST,'details':'Транзакция уже завершена'},status=403)
    rejection_reason = f"Причина: {request.POST.get('rejection_reason')}"
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


@require_POST
def approve_adv_transaction(request,transaction_id):
    """Одобрить заявку на пополнение рекламодателя"""
    transaction = get_object_or_404(AdvertiserTransaction,id=transaction_id)
    if transaction.status == transaction.STATUS_CHOICES.COMPLETED:
        return JsonResponse({"success":False,"data":request.POST,'details':'Транзакция уже завершена'},status=403)
    amount = transaction.amount-((transaction.amount / 100) * Decimal(settings.PARTNER_PAYOUT_SETTINGS["fee_percent"]))
    msg =f"""Здравствуйте!

Мы рады сообщить вам, что ваш баланс был успешно пополнен на сумму {amount}₽ с учётом комиссии {settings.PARTNER_PAYOUT_SETTINGS["fee_percent"]}%. 
Спасибо, что остаетесь с нами! Если у вас есть вопросы или нужна помощь, не стесняйтесь обращаться в нашу службу поддержки.
Id транзакции: {transaction_id}
С уважением,  
Команда LinkOffer"""
    messages.success(request,message="Заявка на пополнение была одобрена!",extra_tags='adv_transaction_success')
    message_list = messages.get_messages(request)
    messages_data = [{"level": message.level_tag, "message": str(message)} for message in message_list]
    transaction.status = AdvertiserTransaction.STATUS_CHOICES.COMPLETED
    transaction.save()
    transaction.advertiser.balance+=amount
    transaction.advertiser.save()
    try:
        send_email_via_mailru.delay(transaction.advertiser.user.email,msg, "Ваш баланс был пополнен!")
    except:
        pass
    AdvertiserActivity.objects.create(
        advertiser=transaction.advertiser,
        activity_type=AdvertiserActivity.ActivityType.TOPUP,
        title='Пополнение баланса',
        details=f'Ваш баланс был пополнен на сумму: {amount}₽ с учётом комиссии {settings.PARTNER_PAYOUT_SETTINGS["fee_percent"]}%.'
    )
    return JsonResponse({"success":True,"data":request.POST,"messages":messages_data},status=200)