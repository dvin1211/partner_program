from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.conf import settings 
from django.utils import timezone

from apps.advertisers.models import AdvertiserTransaction
from apps.core.decorators import role_required
from utils import send_email_via_mailru_with_attachment


proccessed_transaction_msg = """Здравствуйте
    
Мы рады сообщить вам, что ваш запрос на пополнение баланса был успешно обработан.
Реквизиты для перевода прикреплены в файле. Пожалуйста, используйте их для завершения оплаты.

Если у вас возникли вопросы или вам нужна помощь, не стесняйтесь обращаться в нашу службу поддержки.

С уважением,
Команда LinkOffer"""



@role_required('manager')
@require_POST
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
