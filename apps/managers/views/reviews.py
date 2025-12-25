from django.shortcuts import render

from apps.core.models import UserReview
from apps.core.decorators import role_required
from apps.managers.models import ManagerActivity
from utils import _paginate


@role_required('manager')
def reviews(request):
    """Модерация отзывов"""
    user = request.user
    
    reviews = UserReview.objects.filter(status='На модерации').order_by('-created_at')
    reviews_page = _paginate(request,reviews,10,'reviews_page')

    notifications_count = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False).count()

    context = {
        "reviews":reviews_page,
        "reviews_count":reviews.count(),
        "notifications_count":notifications_count
    }

    return render(request,'managers/reviews/reviews.html',context)