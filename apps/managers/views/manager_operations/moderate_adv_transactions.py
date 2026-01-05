from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.conf import settings 
from django.utils import timezone

from apps.advertisers.models import AdvertiserTransaction,AdvertiserActivity
from apps.core.decorators import role_required
from utils import send_email_via_mailru,send_email_via_mailru_with_attachment


proccessed_transaction_msg = """Здравствуйте
    
Мы рады сообщить вам, что ваш запрос на пополнение баланса был успешно обработан.
Реквизиты для перевода прикреплены в файле. Пожалуйста, используйте их для завершения оплаты.

Если у вас возникли вопросы или вам нужна помощь, не стесняйтесь обращаться в нашу службу поддержки.

С уважением,
Команда LinkOffer"""



@require_POST
@role_required('manager')
@transaction.atomic
def proccess_adv_transaction(request, transaction_id):
    """Обработка заявки на пополнение с отправкой реквизитов"""
    
    try:
        # Получаем транзакцию с блокировкой для конкурентных запросов
        transaction_obj = get_object_or_404(
            AdvertiserTransaction.objects.select_for_update()
                                        .select_related('advertiser__user'),
            id=transaction_id
        )
        
        # Проверяем статус транзакции
        if transaction_obj.status == AdvertiserTransaction.STATUS_CHOICES.COMPLETED:
            return JsonResponse({
                "success": False,
                "error": "Транзакция уже завершена"
            }, status=403)
        
        # Проверяем, что транзакция еще не обработана
        if transaction_obj.status == AdvertiserTransaction.STATUS_CHOICES.PROCESSED:
            return JsonResponse({
                "success": False,
                "error": "Реквизиты уже отправлены"
            }, status=400)
        
        # Подготавливаем вложения
        attachments = []
        if 'invoiceFile' in request.FILES:
            uploaded_file = request.FILES['invoiceFile']
            
            # Читаем содержимое файла ДО транзакции
            file_content = uploaded_file.read()
            attachments.append({
                'filename': uploaded_file.name,
                'content': file_content,
                'content_type': uploaded_file.content_type,
            })
        
        # Обновляем статус транзакции (в рамках транзакции)
        transaction_obj.status = AdvertiserTransaction.STATUS_CHOICES.PROCESSED
        transaction_obj.processed_at = timezone.now()
        if request.user.is_authenticated:
            transaction_obj.processed_by = request.user
        transaction_obj.save()
        
        # Отложенная отправка email с вложениями
        def send_email_with_attachments():
            try:
                send_email_via_mailru_with_attachment(
                    transaction_obj.advertiser.user.email,
                    proccessed_transaction_msg,
                    "Счет на оплату для пополнения баланса на вашем аккаунте",
                    attachments
                )
                print(f"Email с реквизитами отправлен для транзакции {transaction_id}")
            except Exception as e:
                print(f"Ошибка отправки email для транзакции {transaction_id}: {e}")
        
        # Выполнится только после успешного сохранения в БД
        transaction.on_commit(send_email_with_attachments)
        
        # Сообщение об успехе
        messages.success(
            request,
            "Реквизиты для пополнения отправлены рекламодателю!",
            extra_tags='adv_transaction_success'
        )
        
        # Подготавливаем данные для ответа
        message_list = messages.get_messages(request)
        messages_data = [
            {"level": message.level_tag, "message": str(message)}
            for message in message_list
        ]
        
        return JsonResponse({
            "success": True,
            "data":request.POST,
            "messages": messages_data
        }, status=200)
        
    except AdvertiserTransaction.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Транзакция не найдена"
        }, status=404)
        
    except Exception as e:
        print(f"Ошибка обработки транзакции {transaction_id}")
        
        
        return JsonResponse({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "detail": str(e) if settings.DEBUG else None
        }, status=500)

@require_POST
@role_required('manager')
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



@require_POST
@role_required('manager')
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