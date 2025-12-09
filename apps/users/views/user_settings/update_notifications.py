from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@login_required
@require_POST
def update_email_notifications(request):
    request.user.email_notifications = 'email_notifications' in request.POST
    request.user.save()
    messages.success(request, message='Настройки уведомлений успешно обновлёны!',extra_tags="update_notifications_success")
    if hasattr(request.user,'advertiserprofile'):
        return redirect('advertiser_settings')    
    elif hasattr(request.user,'partner_profile'):
        return redirect('partner_settings')
    elif hasattr(request.user,'managerprofile'):
        return redirect('manager_settings')