from datetime import timedelta
import re 

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('partner', 'Партнёр'),
        ('advertiser', 'Рекламодатель'),
        ('manager', 'Менеджер')
    )

    middle_name = models.CharField(
        'Отчество',
        max_length=100,
        default=None,
        blank=True,
        null=True 
    )

    email = models.EmailField('email address', unique=True)
    user_type = models.CharField(
        'Тип пользователя',
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='partner' 
    )
    phone = models.CharField(
        'Телефон',
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        default=None
    )
    description = models.CharField(
        'Описание',
        max_length=200,
        default='',
        blank=True
    )
    email_notifications = models.BooleanField(
        'Email уведомления',
        default=False
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    is_blocked = models.BooleanField(default=False)
    blocking_reason = models.CharField(
        'Причина блокировки',
        max_length=100,
        default=None,
        blank=True,
        null=True
    )
    block_until = models.DateTimeField(null=True, blank=True) 
    
    profile_completed = models.BooleanField(default=False, verbose_name="Профиль настроен")

    def block(self, days=None):
        """Блокировать пользователя"""
        self.is_blocked = True
        if days:
            self.block_until = timezone.now() + timedelta(days=days)
        else:
            self.block_until = None  # навсегда
        self.save()

    def unblock(self):
        """Разблокировать пользователя"""
        self.is_blocked = False
        self.block_until = None
        self.save()

    def is_currently_blocked(self):
        """Проверка блокировки"""
        if not self.is_blocked:
            return False
        if self.block_until and timezone.now() > self.block_until:
            self.unblock()
            return False
        return True
    
    def get_ifo(self):
        """Получить имя, фамилию, отчество"""
        return f"{self.first_name} {self.last_name} {self.middle_name}"
    
    def get_fio(self):
        """Получить ФИО"""
        return f"{self.last_name} {self.first_name} {self.middle_name}"
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
    
    def clean(self):
        super().clean()
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', self.email):
            raise ValidationError('Введите корректный email адрес')
        
        if self.phone and not re.match(r'^\+?1?\d{11}$',self.phone):
            raise ValidationError("Телефон должен быть в формате: '+7(999)999-99-99'.")
        
    def save(self,*args,**kwargs):
        self.full_clean()
        super().save(*args,**kwargs)