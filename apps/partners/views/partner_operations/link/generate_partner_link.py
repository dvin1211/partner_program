from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import IntegrityError

from apps.core.decorators import role_required
from apps.partners.models import PartnerLink
from apps.partnerships.models import ProjectPartner

@role_required('partner')
@require_POST
def generate_link(request, partnership_id):
    try:
        partnership = get_object_or_404(ProjectPartner, id=partnership_id)
        
        generated_link = request.POST.get('generated_link', '').strip()
        generated_id = int(request.POST.get('fixedPidInput','0').strip())
        
        if generated_id <= 0:
            messages.error(request, "Id ссылки должен быть больше 0",extra_tags="generate_link_error")
            return redirect('partner_connections')
        # Валидация ссылки
        if not generated_link:
            messages.error(request, "Ссылка не может быть пустой",extra_tags="generate_link_error")
            return redirect('partner_connections')
        
        if not generated_link.startswith(('http://', 'https://')):
            messages.error(request, "Ссылка должна начинаться с http:// или https://",extra_tags="generate_link_error")
            return redirect('partner_connections')
        
        # Проверка, что ссылка уже не существует
        if PartnerLink.objects.filter(url=generated_link, partnership=partnership).exists():
            messages.error(request, "Такая ссылка уже существует",extra_tags="generate_link_error")
            return redirect('partner_connections')
        
        # Создание ссылки
        partner_link = PartnerLink.objects.create(
            id=generated_id,
            partner=request.user,
            project=partnership.project,
            partnership=partnership,
            url=generated_link,
        )
        
        partnership.partner_link = partner_link
        partnership.save()
        
        messages.success(request, "Партнёрская ссылка успешно сгенерирована!",extra_tags="generate_link_success")
        return redirect('partner_connections')
        
    except IntegrityError:
        messages.error(request, "Ошибка базы данных при создании ссылки",extra_tags="generate_link_error")
        return redirect('partner_connections')
    except Exception as e:
        print(f"Unexpected error: {e}")
        messages.error(request, f"Произошла непредвиденная ошибка: {e}",extra_tags="generate_link_error")
        return redirect('partner_connections')