from django.db import models
from django.core.validators import MinValueValidator
from django.utils.functional import cached_property
from typing import Any, Optional


class AdvertiserProfile(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    api_key = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True, 
        default=None, 
        verbose_name="API-ключ"
    )
    balance = models.DecimalField(
        verbose_name="Мин. выплата",
        decimal_places=2,
        default=0.00, 
        max_digits=10,
        validators=[MinValueValidator(0.00)],
    )
    
    BASIC_FIELDS_CONFIG = [
        {'name': 'Имя', 'field': 'first_name'},
        {'name': 'Фамилия', 'field': 'last_name'},
        {'name': 'Телефон', 'field': 'phone'},
    ]
    
    REQUISITES_FIELDS_CONFIG = [
        {'name': 'Ответственное лицо', 'field': 'responsible_person'},
        {'name': 'Полное наименование организации', 'field': 'organization_name'},
        {'name': 'Телефон', 'field': 'phone'},
        {'name': 'Почта', 'field': 'email'},
        {'name': 'ОГРН', 'field': 'ogrn'},
        {'name': 'ИНН', 'field': 'inn'},
        {'name': 'Расчётный счёт', 'field': 'checking_account'},
        {'name': 'Корреспондентский счёт', 'field': 'correspondent_account'},
        {'name': 'БИК', 'field': 'bik'},
    ]

    def is_complete_profile(self) -> bool:
        """Проверяет, заполнены ли все обязательные поля"""
        
        # 1. Проверка флага профиля (если уже завершен)
        if getattr(self.user, 'profile_completed', False):
            return True
        
        # 2. Проверка основных полей пользователя
        basic_fields_complete = self._check_basic_fields()
        if not basic_fields_complete:
            return False
        
        # 3. Проверка реквизитов
        requisites_complete = self._check_requisites_fields()
        if not requisites_complete:
            return False
        
        # 4. Все проверки пройдены - помечаем профиль как завершенный
        self.user.profile_completed = True
        self.user.save(update_fields=['profile_completed'])
        
        return True

    def _check_basic_fields(self) -> bool:
        """Проверяет заполненность основных полей пользователя"""
        required_fields = ['first_name', 'last_name', 'phone']
        
        for field_name in required_fields:
            value = getattr(self.user, field_name, None)
            
            # Более строгая проверка для строк
            if not value or (isinstance(value, str) and not value.strip()):
                return False
        
        return True

    def _check_requisites_fields(self) -> bool:
        """Проверяет заполненность полей реквизитов"""
        REQUIRED_REQUISITES_FIELDS = [
            'responsible_person',
            'organization_name', 
            'phone',
            'email',
            'ogrn',
            'inn',
            'checking_account',
            'correspondent_account',
            'bik'
        ]
        
        # Проверяем наличие реквизитов
        if not hasattr(self.user, 'advertiserrequisites'):
            return False
        
        requisites = self.user.advertiserrequisites
        
        # Проверяем все поля за один проход с ранним выходом
        for field_name in REQUIRED_REQUISITES_FIELDS:
            value = getattr(requisites, field_name, None)
            
            # Универсальная проверка заполненности
            if not value or (isinstance(value, str) and not value.strip()):
                return False  # Ранний выход при первой же ошибке
        
        return True

    @cached_property
    def advertiser_requisites(self) -> Optional[models.Model]:
        """Кэшированный доступ к реквизитам"""
        if hasattr(self.user, 'advertiserrequisites'):
            return self.user.advertiserrequisites
        return None
    
    def _get_field_status(self, field_name: str, field_value: Any) -> dict[str, Any]:
        """Утилита для получения статуса одного поля"""
        return {
            'is_filled': bool(field_value and str(field_value).strip()),
            'value': field_value or '',
        }
    
    def _get_basic_fields_status(self) -> list[dict[str, Any]]:
        """Статус основных полей пользователя"""
        fields_status = []
        
        for field_config in self.BASIC_FIELDS_CONFIG:
            field_value = getattr(self.user, field_config['field'], None)
            field_status = self._get_field_status(field_config['field'], field_value)
            fields_status.append({
                'name': field_config['name'],
                'field': field_config['field'],
                **field_status
            })
        
        return fields_status
    
    def _get_requisites_status(self) -> list[dict[str, Any]]:
        """Статус полей реквизитов"""
        requisites = self.advertiser_requisites
        
        if not requisites:
            return [
                {
                    'name': config['name'],
                    'field': config['field'],
                    'value': '',
                    'is_filled': False,
                }
                for config in self.REQUISITES_FIELDS_CONFIG
            ]
        
        fields_status = []
        for config in self.REQUISITES_FIELDS_CONFIG:
            field_value = getattr(requisites, config['field'], '')
            
            if config['field'] in ['responsible_person', 'phone']:
                field_value = field_value or ''
            
            field_status = self._get_field_status(config['field'], field_value)
            fields_status.append({
                'name': config['name'],
                'field': config['field'],
                **field_status
            })
        
        return fields_status
    
    def get_progress(self):
        basic_fields = self._get_basic_fields_status()
        requisites_fields = self._get_requisites_status()
        all_fields = basic_fields + requisites_fields
        filled_count = sum(1 for f in all_fields if f['is_filled'])
        total_count = len(all_fields)
        return int((filled_count / total_count) * 100) if total_count > 0 else 0

    def get_profile_status(self) -> dict[str, Any]:
        """Возвращает статус заполнения каждого поля в профиле"""
        basic_fields = self._get_basic_fields_status()
        filled_count = sum(1 for f in basic_fields if f['is_filled'])
        
        total_count = len(basic_fields)
        progress_percentage = int((filled_count / total_count) * 100) if total_count > 0 else 0
        
        return {
            'fields': basic_fields,
            'progress': progress_percentage,
            'filled_count': filled_count,
            'total_count': total_count
        }
    
    def get_requisites_status(self):
        """Возвращает статус заполнения каждого поля в реквизитах"""
        basic_fields = self._get_requisites_status()
        filled_count = sum(1 for f in basic_fields if f['is_filled'])
        
        total_count = len(basic_fields)
        progress_percentage = int((filled_count / total_count) * 100) if total_count > 0 else 0
        return {
            'fields': basic_fields,
            'progress': progress_percentage,
            'filled_count': filled_count,
            'total_count': total_count
        }

    @cached_property
    def conversions_percent(self) -> str:
        """Процент конверсий"""
        clicks_count = self.clicks_count
        if clicks_count == 0:
            return "0.00"
        
        conversions_count = self.conversions_count
        percent = (conversions_count / clicks_count) * 100
        return f"{percent:.2f}"
    
    @cached_property
    def conversions_count(self) -> int:
        """Количество конверсий (кэшируется)"""
        return self.conversions.count()
    
    @cached_property
    def clicks_count(self) -> int:
        """Количество кликов (кэшируется)"""
        return self.clicks.count()
    
    def save(self, *args, **kwargs):
        """Переопределяем save для инвалидации кэша при изменении"""
        if hasattr(self, '_conversions_count_cache'):
            delattr(self, '_conversions_count_cache')
        if hasattr(self, '_clicks_count_cache'):
            delattr(self, '_clicks_count_cache')
        if hasattr(self, '_advertiser_requisites_cache'):
            delattr(self, '_advertiser_requisites_cache')
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Рекламодатель'
        verbose_name_plural = 'Рекламодатели'

    def __str__(self) -> str:
        username = getattr(self.user, 'username', 'Неизвестно')
        return f"Профиль: {username}"