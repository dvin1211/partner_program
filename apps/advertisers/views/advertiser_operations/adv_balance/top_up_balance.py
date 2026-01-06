from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.advertisers.models import AdvertiserTransaction
from apps.core.decorators import role_required


@role_required('advertiser')
@require_POST
def top_up_balance(request):
    """Пополнение баланса у рекламодателя"""
    try:
        if hasattr(request.user,'advertiserprofile'):
            if float(request.POST.get("amount")) < float(settings.PARTNER_PAYOUT_SETTINGS["min_amount"]):
                messages.error(request,message="Сумма пополнения не должна быть меньше 300₽",extra_tags='top_up_error')
                request_status = 403
                success = False
            else: 
                transaction = AdvertiserTransaction.objects.create(
                    advertiser=request.user.advertiserprofile,
                    amount=request.POST.get('amount'),
                    payment_method=request.POST.get('transaction_payout_method'))
                transaction.save()
                messages.success(request,message="Заявка на пополнение создана",extra_tags='top_up_success')
                request_status = 201
                success = True
        else:
            messages.error(request,message="Доступ запрещён",extra_tags='top_up_error')
            request_status = 403
            success = False
            

        message_list = messages.get_messages(request)
        messages_data = [{"level": message.level_tag, "message": str(message)} for message in message_list]
        return JsonResponse({"success":success,"messages":messages_data,"data":request.POST},status=request_status)
    except Exception as e:
        messages.success(request,message=f"Заявка на пополнение не была создана:{e}",extra_tags='top_up_error')
        return JsonResponse({"success":False,"error":e},status=500)