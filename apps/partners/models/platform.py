from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone


class Platform(models.Model):
    class PlatformType(models.TextChoices):
        WEBSITE = 'website', 'Веб-сайт'
        SOC_NETWORKS = 'social_networks', 'Социальные сети'
        YOUTUBE = 'youtube', 'YouTube'
        BLOG = 'blog', 'Блог'
        OTHER = 'other', 'Другое'

    class StatusType(models.TextChoices):
        PENDING = 'На модерации'
        APPROVED = 'Подтверждено'
        REJECTED = 'Отклонено'
        BLOCKED = 'Заблокировано'
        DELETED = 'Удалено'

    partner = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='owned_platforms',
        verbose_name='Партнёр',
        limit_choices_to={'user_type': 'partner'},
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название площадки',
        validators=[MinLengthValidator(3)],
        help_text='Например: TikTok-канал о кулинарии'
    )

    description = models.CharField(
        max_length=200,
        verbose_name="Описание площадки",
        validators=[MinLengthValidator(15)],
        help_text="Например: Блог о путешествиях"
    )

    platform_type = models.CharField(
        max_length=20,
        choices=PlatformType.choices,
        verbose_name='Тип площадки',
    )
    url_or_id = models.CharField(
        max_length=150,
        verbose_name='URL или ID',
        help_text='Ссылка или идентификатор (@username, channel ID)'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        verbose_name='Дата удаления',
        help_text='Дата мягкого удаления записи. NULL если запись активна.'
    )

    status = models.CharField(
        default="На модерации",
        choices=StatusType,
        verbose_name='Статус'
    )

    is_active = models.BooleanField(default=True)
    
    def soft_delete(self):
        """Мягкое удаление записи"""
        self.deleted_at = timezone.now()
        self.status = self.StatusType.DELETED
        self.is_active = False
        self.save()

    @property
    def conversions_count(self):
        return self.conversions.count()
    
    @property 
    def conversions_percent(self):
        if self.clicks.count() == 0:
            return 0.0
        return f"{(self.conversions.count() / self.clicks.count()) * 100:.2f}"
    
    @property
    def clicks_count(self):
        return self.clicks.count()
    
    class Meta:
        verbose_name = 'Площадка'
        verbose_name_plural = 'Площадки'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['partner', 'url_or_id'],
                name='unique_platform'
            )
        ]
        indexes = [
            models.Index(fields=['deleted_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_platform_type_display()})"