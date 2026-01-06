from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.core.decorators import role_required
from apps.partners.models import Platform


@role_required('partner')
@require_POST
def edit_platform(request,platform_id):
    """Изменить платформу"""
    platform = get_object_or_404(Platform,id=platform_id,partner=request.user)
    try:
        platform.name = request.POST.get('name', platform.name)
        platform.url_or_id = request.POST.get('url', platform.url_or_id)
        platform.platform_type = request.POST.get('type',platform.platform_type)
        platform.description = request.POST.get('description', platform.description)
        if request.POST.get('is_active',None):
            platform.is_active = True
        else:
            platform.is_active = False
        # Валидация
        platform.full_clean()
        platform.save()
        messages.success(request,message=f"Платформа {platform.name} успешно отредактирована",extra_tags="platform_edit_success")
        return redirect("partner_platforms")
    except Exception as e:
        for num,(field,error) in enumerate(e.message_dict.items()):
            messages.error(request, f"{num+1}. {field} : {error[0]}",extra_tags="platform_edit_error")
    return redirect("partner_platforms")