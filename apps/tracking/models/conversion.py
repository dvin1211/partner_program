from django.db import models

class Conversion(models.Model):
    project = models.ForeignKey(
        'advertisers.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversions'
    )
    advertiser = models.ForeignKey(
        'advertisers.AdvertiserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversions'
    )
    partner = models.ForeignKey(
        'partners.PartnerProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversions'
    )
    partner_link = models.ForeignKey(
        'partners.PartnerLink',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversions'
    )
    platform = models.ForeignKey(
        'partners.Platform',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversions'
    )
    
    partnership = models.ForeignKey(
        'partnerships.ProjectPartner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='conversions',
        verbose_name="Сотрудничество партнёра с проектом"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма конверсии'
    )
    created_at = models.DateTimeField(auto_now_add=True,)
    details = models.TextField(blank=True)
    
    referrer = models.URLField(null=True, blank=True,default=None, verbose_name="Источник")
    user_agent = models.TextField(null=True, blank=True, verbose_name="User-Agent")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP-адрес")

    class Meta:
        verbose_name ="Конверсия"
        verbose_name_plural ="Конверсии"
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['partner']),
            models.Index(fields=['partnership']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Конверсия #{self.id} (Партнёр: {self.partner})"