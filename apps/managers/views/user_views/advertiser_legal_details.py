from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from apps.users.models import User


@login_required
def advertiser_legal_details(request, advertiser_id):
    if not hasattr(request.user,'managerprofile'):
        return redirect('dashboard')
    advertiser = get_object_or_404(
        User,id=advertiser_id
    )
    
    # Проверка прав доступа
    if not hasattr(advertiser, 'advertiserprofile'): 
        messages.error(request, message="Этот пользователь не является рекламодателем")
        if hasattr(request.user, 'advertiserprofile'): 
            return redirect('advertiser_dashboard')
        return redirect('dashboard')

    context = {
        'advertiser': advertiser,
    }
    return render(request, 'managers/advertisers_requisites/advertiser_requisites.html', context)