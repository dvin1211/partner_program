from django.db import models
from django.utils.translation import gettext_lazy as _


class ManagerActivity(models.Model):
    class ActivityType(models.TextChoices):
        PROJECT = 'project', _('Проект')
        PLATFORM = 'platform', _('Платформа')
        NEW_USER = 'new_user', _('Новый пользователь')
        PAYOUT = 'payout', _('Выплата')
        TOPUP = 'top_up', ('Пополнение баланса')
        REVIEW = 'review', ('Отзыв')
        SYSTEM = 'system', _('Системное уведомление')
        OTHER = 'other', _('Другое')

    manager = models.ForeignKey(
        'managers.ManagerProfile',
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('Менеджер')
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        verbose_name=_('Тип активности')
    )
    title = models.CharField(
        max_length=100,
        verbose_name=_('Заголовок')
    )
    details = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Детали')
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Прочитано')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Активность менеджра')
        verbose_name_plural = _('Активности менеджеров')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['manager', 'is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.manager}"