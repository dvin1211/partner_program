from django.views.decorators.http import require_POST
from django.http import JsonResponse

from apps.core.decorators import role_required
from apps.core.models import UserReview

# Опубликовать отзыв
@role_required('manager')
@require_POST
def publish_review(request,review_id):
    """Опубликовать отзыв"""
    review = UserReview.objects.get(id=review_id)
    review.status = review.StatusType.PUBLISHED
    review.save()
    return JsonResponse({"success":True},status=200)