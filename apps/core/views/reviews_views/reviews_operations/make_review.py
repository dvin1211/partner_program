from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from apps.core.models import UserReview

@require_POST
def make_review(request):
    """Оставить отзыв на сайте"""
    name = request.POST.get('reviewerName')
    rating = int(request.POST.get('rating'))
    comment = request.POST.get('reviewText')
    user = None 
    if request.user.is_authenticated:
        user = request.user
    review = UserReview.objects.create(name=name,rating=rating,comment=comment,user=user)
    review.save()
    return JsonResponse({"success":True})