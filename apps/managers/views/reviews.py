from django.shortcuts import render

from apps.core.models import UserReview
from apps.core.decorators import role_required
from apps.managers.views.utils import get_manager_stats
from utils import _paginate


@role_required('manager')
def reviews(request):
    """Модерация отзывов"""
    user = request.user
    
    reviews = UserReview.objects.filter(status='На модерации').order_by('-created_at')
    reviews_page = _paginate(request,reviews,10,'reviews_page')

    context = {
        "reviews":reviews_page,
        "reviews_count":reviews.count(),
        
        **get_manager_stats(user)
    }

    return render(request,'managers/reviews/reviews.html',context)