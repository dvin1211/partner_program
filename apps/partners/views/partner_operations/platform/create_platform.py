from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.core.decorators import role_required
from apps.partners.forms import PlatformForm

@role_required('partner')
@require_POST
def add_platform(request):
    form = PlatformForm(request.POST)
    try:
        platform = form.save(commit=False)
        platform.partner = request.user
        platform.save()
        messages.success(request,message=f"Платформа {platform.name} успешно добавлена",extra_tags="platform_add_success")
        return redirect("partner_platforms")
    except Exception as e:
        if "description" in form.errors:
            messages.error(request, message="Описание должно содержать минимум 15 символов.",extra_tags="platform_add_error")
        else:
            messages.error(request, message="Уже существует площадка с таким  URL или названием.",extra_tags="platform_add_error")
    return redirect("partner_platforms")