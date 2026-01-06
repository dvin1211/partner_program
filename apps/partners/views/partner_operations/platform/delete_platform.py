from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.core.decorators import role_required
from apps.partners.models import Platform



@role_required('partner')
@require_POST
def delete_platform(request, platform_id):
    try:
        platform = get_object_or_404(Platform,id=platform_id,partner=request.user)
        platform.soft_delete()
        messages.success(request,message=f"Платформа {platform.name} успешно удалена",extra_tags="platform_delete_success")
    except Exception as e:
        messages.error(request, message=f"Ошибка удаления платформы: {e}",extra_tags="platform_delete_error")
    return redirect("partner_platforms")
