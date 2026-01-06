from django.views.decorators.http import require_POST
from django.http import JsonResponse

from apps.core.decorators import role_required
from apps.core.models import UserReview


# Изменить текст отзыва
@role_required('manager')
@require_POST
def edit_review(request,review_id):
    """Изменить текст отзыва"""
    review = UserReview.objects.get(id=review_id)
    comment = request.POST['review_comment']
    review.comment = comment
    review.save()
    return JsonResponse({"success":True},status=200)
