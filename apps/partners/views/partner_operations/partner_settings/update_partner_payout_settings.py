import asyncio

from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction

from apps.core.decorators import role_required
from apps.partners.models import PartnerPayoutSettings
from utils import fetch_bank_data

@role_required('partner')
@require_POST
def payout_settings_view(request):
    user = request.user
    if not hasattr(user, 'partner_profile'):
        messages.error(request, "Доступ запрещён.")
        return redirect('dashboard')
    
    payout_method = request.POST.get('payout_method', None)
    
    if payout_method not in dict(PartnerPayoutSettings.PAYOUT_METHOD_CHOICES) or payout_method.strip() is None:
        messages.error(request, message="Выберите корректный способ вывода средств.", extra_tags="payout_settings_error")
        return redirect('partner_settings')

    # Начинаем транзакцию для атомарности
    with transaction.atomic():
        try:
            # Пытаемся получить существующие настройки партнера
            settings_obj = PartnerPayoutSettings.objects.get(partner=user)
            
            # Обновляем способ выплат
            settings_obj.payout_method = payout_method
            settings_obj.active_payout_method = payout_method
            
        except PartnerPayoutSettings.DoesNotExist:
            # Если настроек нет, создаем новую запись
            settings_obj = PartnerPayoutSettings(
                partner=user,
                payout_method=payout_method,
                active_payout_method=payout_method
            )
            

        # Обновляем поля в зависимости от способа
        if payout_method == 'card':
            settings_obj.card_number = request.POST.get('card_number')
            settings_obj.cardholder_name = request.POST.get('cardholder_name')
            
            try:
                settings_obj.bank_name = asyncio.run(fetch_bank_data(request.POST.get('card_number')))
            except:
                settings_obj.bank_name = None

        elif payout_method == 'bank_transfer':
            settings_obj.bank_account_number = request.POST.get('bank_account_number')
            settings_obj.bank_account_holder_name = request.POST.get('bank_account_holder_name')
            settings_obj.bank_account_bic = request.POST.get('bank_bic_transfer')

        elif payout_method == 'e_wallet':
            settings_obj.e_wallet_identifier = request.POST.get('e_wallet_identifier')

        elif payout_method == 'sbp':
            settings_obj.sbp_identifier = request.POST.get('sbp_identifier')

        settings_obj.save()
        messages.success(request, message="Настройки вывода средств сохранены.", extra_tags='payout_settings_success')
        return redirect('partner_settings')