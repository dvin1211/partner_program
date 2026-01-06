from django.views.decorators.http import require_POST
from django.http import JsonResponse

from apps.core.decorators import role_required
from apps.core.models import UserReview

# Удалить отзыв
@role_required('manager')
@require_POST
def remove_review(request,review_id):
    """Удалить отзыв"""
    review = UserReview.objects.get(id=review_id)
    review.delete()
    return JsonResponse({"success":True},status=200)