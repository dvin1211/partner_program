from decimal import Decimal

from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.validators import MinValueValidator
from django.http import JsonResponse

from apps.core.decorators import role_required
from apps.partners.models import PartnerTransaction


@role_required('partner')
@require_POST
def create_payout_request(request):
    """Создать заявку на вывод средств партнёра"""
    
    user = request.user
    if not hasattr(user, 'partner_profile'):
        return redirect('index')

    # Получаем данные из формы
    amount_str = request.POST.get('amount')
    payout_method = request.POST.get('transaction_payout_method')

    # Проверяем сумму
    try:
        amount = Decimal(amount_str)
        MinValueValidator(Decimal('0.01'))(amount)
    except Exception:
        messages.error(request, message='Введите корректную сумму.',extra_tags='create_payout_error')
        if request.POST.get('referrer') == "quick_withdraw":
            success = False
            request_status = 403
            message_list = messages.get_messages(request)
            messages_data = [{"level": message.level_tag, "message": str(message)} for message in message_list]
            return JsonResponse({"success":success,"messages":messages_data,"data":request.POST},status=request_status)
        return redirect('partner_payments')

    # Проверяем, что сумма не превышает баланс партнёра
    balance = user.partner_profile.balance
    
    if amount < float(settings.PARTNER_PAYOUT_SETTINGS["min_amount"]):
        messages.error(request, message='Сумма превышает доступный баланс.',extra_tags='create_payout_error')
        if request.POST.get('referrer') == "quick_withdraw":
            success = False
            request_status = 403
            message_list = messages.get_messages(request)
            messages_data = [{"level": message.level_tag, "message": str(message)} for message in message_list]
            return JsonResponse({"success":success,"messages":messages_data,"data":request.POST},status=request_status)
        return redirect('partner_payments')
    
    if amount > balance:
        messages.error(request, message='Сумма превышает доступный баланс.',extra_tags='create_payout_error')
        if request.POST.get('referrer') == "quick_withdraw":
            success = False
            request_status = 403
            message_list = messages.get_messages(request)
            messages_data = [{"level": message.level_tag, "message": str(message)} for message in message_list]
            return JsonResponse({"success":success,"messages":messages_data,"data":request.POST},status=request_status)
        return redirect('partner_payments')
    
    # Проверяем выбранный способ вывода
    valid_methods = [choice[0] for choice in PartnerTransaction.PAYMENT_METHOD_CHOICES]
    if payout_method not in valid_methods:
        messages.error(request, message='Выберите корректный способ выплаты.',extra_tags='create_payout_error')
        if request.POST.get('referrer') == "quick_withdraw":
            success = False
            request_status = 403
            message_list = messages.get_messages(request)
            messages_data = [{"level": message.level_tag, "message": str(message)} for message in message_list]
            return JsonResponse({"success":success,"messages":messages_data,"data":request.POST},status=request_status)
        return redirect('partner_payments')

    # Создаём заявку на выплату
    PartnerTransaction.objects.create(
        partner=user,
        amount=amount,
        payment_method=payout_method,
        status='В обработке'
    )

    # Обновляем баланс пользователя 
    user.partner_profile.balance -= amount
    user.partner_profile.save()
    messages.success(request, message=f'Заявка на выплату {amount} ₽ создана успешно.',extra_tags='create_payout_success')
    if request.POST.get('referrer') == "quick_withdraw":
        success = True
        request_status = 201
        message_list = messages.get_messages(request)
        messages_data = [{"level": message.level_tag, "message": str(message)} for message in message_list]
        return JsonResponse({"success":success,"messages":messages_data,"data":request.POST},status=request_status)
    return redirect('partner_payments') 