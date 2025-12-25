from django.db import models
from django.core.validators import MinValueValidator

class PartnerProfile(models.Model):
    user = models.OneToOneField(
        'users.User', 
        on_delete=models.CASCADE,
        related_name='partner_profile',
        verbose_name='Пользователь'
    )
    balance = models.DecimalField(
        verbose_name="Баланс",
        decimal_places=2,
        default=0.00, 
        max_digits=10,
        validators=[MinValueValidator(0.00)],
    )

    def is_complete_profile(self):
        """Проверяет, заполнены ли все обязательные поля"""
        
        if self.user.profile_completed: return True
        
        basic_fields = [
            self.user.first_name,
            self.user.last_name,
            self.user.phone,
        ]
        
        # Проверка основных полей
        basic_complete = all(field and str(field).strip() for field in basic_fields)
        
        # НОВАЯ ПРОВЕРКА: хотя бы один способ вывода должен быть настроен
        payout_complete = False
        
        if hasattr(self.user, 'payout_settings'):
            payout_settings = self.user.payout_settings
            
            # Проверяем, что выбран способ выплат
            if payout_settings.payout_method:
                # Проверяем заполненность полей в зависимости от выбранного способа
                if payout_settings.payout_method == 'card':
                    payout_complete = all([
                        payout_settings.card_number,
                        payout_settings.cardholder_name
                    ])
                elif payout_settings.payout_method == 'bank_transfer':
                    payout_complete = all([
                        payout_settings.bank_account_number,
                        payout_settings.bank_account_holder_name,
                        payout_settings.bank_account_bic
                    ])
                elif payout_settings.payout_method == 'e_wallet':
                    payout_complete = bool(payout_settings.e_wallet_identifier)
                elif payout_settings.payout_method == 'sbp':
                    payout_complete = bool(payout_settings.sbp_identifier)
        
        if basic_complete and payout_complete:
            self.user.profile_completed = True 
            self.user.save()
            return True
        return False
    
    def get_profile_status(self):
        """Возвращает статус заполнения каждого поля"""
        fields_status = [
            {
                'name': 'Имя',
                'field': 'first_name',
                'value': self.user.first_name,
                'is_filled': bool(self.user.first_name and str(self.user.first_name).strip()),
                'is_user_field': True
            },
            {
                'name': 'Фамилия',
                'field': 'last_name',
                'value': self.user.last_name,
                'is_filled': bool(self.user.last_name and str(self.user.last_name).strip()),
                'is_user_field': True
            },
            {
                'name': 'Телефон',
                'field': 'phone',
                'value': self.user.phone,
                'is_filled': bool(self.user.phone and str(self.user.phone).strip()),
                'is_user_field': False
            }
        ]
        
        # Добавляем проверку способа вывода
        payout_status = self._get_payout_status()
        fields_status.append(payout_status)
        
        # Пересчитываем прогресс
        required_fields = [f for f in fields_status if not f.get('is_optional', False)]
        filled_count = sum(1 for f in required_fields if f['is_filled'])
        progress_percentage = int((filled_count / len(required_fields)) * 100) if required_fields else 0
        return {
            'fields': fields_status,
            'progress': progress_percentage,
            'filled_count': filled_count,
            'total_count': len(required_fields)
        }

    def _get_payout_status(self):
        """Возвращает статус настроек выплат"""
        if not hasattr(self.user, 'payout_settings'):
            return {
                'name': 'Способ выплат',
                'field': 'payout_method',
                'is_filled': False,
                'is_optional': False,
                'details': 'Настройки выплат не найдены',
                'method': None
            }
        
        payout_settings = self.user.payout_settings
        
        # Проверяем выбран ли способ
        if not payout_settings.payout_method:
            return {
                'name': 'Способ выплат',
                'field': 'payout_method',
                'is_filled': False,
                'is_optional': False,
                'details': 'Способ выплат не выбран',
                'method': None
            }
        
        # Проверяем заполненность в зависимости от способа
        is_filled = False
        method_name = payout_settings.get_payout_method_display()
        details = ""
        
        if payout_settings.payout_method == 'card':
            is_filled = all([
                payout_settings.card_number,
                payout_settings.cardholder_name
            ])
            details = f"Карта: {payout_settings.masked_card() if payout_settings.card_number else 'номер не указан'}"
            
        elif payout_settings.payout_method == 'bank_transfer':
            is_filled = all([
                payout_settings.bank_account_number,
                payout_settings.bank_account_holder_name,
                payout_settings.bank_account_bic
            ])
            details = f"Банковский счёт: {payout_settings.bank_account_number[-4:] if payout_settings.bank_account_number else 'не указан'}"
            
        elif payout_settings.payout_method == 'e_wallet':
            is_filled = bool(payout_settings.e_wallet_identifier)
            details = f"Электронный кошелёк: {payout_settings.e_wallet_identifier or 'не указан'}"
            
        elif payout_settings.payout_method == 'sbp':
            is_filled = bool(payout_settings.sbp_identifier)
            details = f"СБП: {payout_settings.sbp_identifier or 'не указан'}"
        return {
            'name': 'Способ выплат',
            'field': 'payout_method',
            'is_filled': is_filled,
            'is_optional': False,
            'details': details,
            'method': payout_settings.payout_method,
            'method_display': method_name
        }

    @property 
    def conversions_percent(self):
        if self.clicks.count() == 0:
            return 0.0
        return f"{(self.conversions.count() / self.clicks.count()) * 100:.2f}"
    
    @property
    def conversions_count(self):
        return self.conversions.count()

    @property
    def clicks_count(self):
        return self.clicks.count() 
    
    class Meta:
        verbose_name = 'Партнёр'
        verbose_name_plural = 'Партнёры'

    def __str__(self):
        return f"Профиль: {self.user.username}" if self.user else "Непривязанный профиль"
