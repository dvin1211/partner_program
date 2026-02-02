from django.db.models import Q

from apps.advertisers.models import Project, AdvertiserTransaction
from apps.partners.models import Platform, PartnerTransaction
from apps.core.models import UserReview
from apps.managers.models import ManagerActivity


def get_manager_stats(user):
    """Получить статистику менеджера"""
    pending_projects_count = Project.objects.filter(status='На модерации').count()
    pending_platforms_count = Platform.objects.filter(status='На модерации').count()
    partner_transactions_count = PartnerTransaction.objects.filter(status='В обработке').count()
    advertiser_transactions_count = AdvertiserTransaction.objects.filter(Q(status='В обработке') | Q(status='Обработано')).count()
    reviews_count = UserReview.objects.filter(status=UserReview.StatusType.PENDING).count()
    notifications_count = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False).count()

    return {
        "pending_projects_count":pending_projects_count,
        "pending_platforms_count":pending_platforms_count,
        "partner_transactions_count":partner_transactions_count,
        "advertiser_transactions_count":advertiser_transactions_count,
        "reviews_count":reviews_count,
        "notifications_count":notifications_count
    }
    