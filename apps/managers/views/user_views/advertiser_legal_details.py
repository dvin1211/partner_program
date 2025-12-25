from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from apps.core.decorators import role_required
from apps.users.models import User


@role_required('manager')
def advertiser_legal_details(request, advertiser_id):
    advertiser = get_object_or_404(
        User,id=advertiser_id
    )
    
    if not hasattr(advertiser, 'advertiserprofile'): 
        messages.error(request, message="Этот пользователь не является рекламодателем")
        return redirect('dashboard')

    context = {
        'advertiser': advertiser,
    }
    return render(request, 'managers/advertisers_requisites/advertiser_requisites.html', context)