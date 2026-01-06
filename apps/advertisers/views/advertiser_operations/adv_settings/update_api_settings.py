from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST

from apps.advertisers.forms import ApiSettingsForm
from apps.core.decorators import role_required


@role_required('advertiser')
@require_POST
def update_api_settings(request):
    form = ApiSettingsForm(request.POST, request=request)
    if form.is_valid():
        request.user.advertiserprofile.api_key = form.cleaned_data['api_key']
        request.user.advertiserprofile.save()
        messages.success(request, message='API ключ успешно обновлён!',extra_tags="update_api_success")
        return redirect('advertiser_settings')
    else:
        messages.error(request, message="Ошибка: " + str(form.errors), extra_tags="update_api_error")
    return redirect('advertiser_settings')