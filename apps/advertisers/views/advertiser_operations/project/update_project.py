from decimal import Decimal

from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.advertisers.models import Project
from apps.core.decorators import role_required
from apps.partnerships.models import ProjectPartner
from utils import mass_mailing


@role_required('advertiser')
@require_POST   
def edit_project(request,project_id):
    project = get_object_or_404(
        Project,
        id=project_id,
        advertiser=request.user
    )

    old_price = Decimal(project.cost_per_action)
    old_is_active = project.is_active
    
    project.name = request.POST.get('name', project.name).strip()
    project.description = request.POST.get('description', project.description).strip()
    project.action_name = request.POST.get('customActionName', project.action_name).strip()
        
    try:
        new_price = Decimal(request.POST.get('costPerAction', old_price))
    except Exception:
        messages.error(request, "Неверный формат цены", extra_tags="project_edit_error")
        return redirect("advertiser_projects")
    new_is_active = request.POST.get('is_active') == 'on'

    try:
        price_changed = False
        if new_price != old_price:
            max_allowed = old_price * Decimal('2')
            min_allowed = old_price * Decimal('0.5') 
            if new_price > max_allowed or new_price < min_allowed:
                project.new_cost_per_action = Decimal(new_price)
                project.status = project.StatusType.PENDING
                messages.warning(
                    request, 
                    message=f"Проект '{project.name}' отправлен на модерацию из-за изменения цены", 
                    extra_tags="project_edit_success"
                )
                price_changed = True
            else:
                project.cost_per_action = new_price
                messages.success(
                    request,
                    message=f"Цена проекта '{project.name}' успешно обновлена",
                    extra_tags="project_edit_success"
                )
        if old_is_active != new_is_active:
            if new_is_active:
                make_bulk_mailing(request.user, project, "make_active")
                messages.info(
                    request,
                    message=f"Проект '{project.name}' активирован. Партнеры уведомлены.",
                    extra_tags="project_edit_success"
                )
            else:
                make_bulk_mailing(request.user, project, "make_not_active")
                messages.warning(
                    request,
                    message=f"Проект '{project.name}' приостановлен. Партнеры уведомлены.",
                    extra_tags="project_edit_success"
                )
            project.is_active = new_is_active
        if price_changed:
            make_bulk_mailing(
                request.user, 
                project, 
                "change_price",
                extra_data={'old_price': old_price, 'new_price': new_price}
            )
        project.save()
    except Exception as e:
        print(type(e),e)
        messages.error(request, f"Ошибка редактирования проекта: {str(e)}",extra_tags="project_edit_error")
        return redirect("advertiser_projects")
    
    
    messages.success(request,message=f"Проект {project.name} успешно отредактирован",extra_tags="project_edit_success")
    return redirect("advertiser_projects")


def make_bulk_mailing(user,project,type_mailing):
    """Массовая рассылка"""
    partnerships = ProjectPartner.objects.filter(
                    project=project
                ).select_related('partner')
                
    project_name = project.name
    advertiser_name = user.username

    recipients_data = []
    message = None

    for partnership in partnerships:
        partner_email = partnership.partner.email
        partner_name = partnership.partner.username

        if type_mailing == 'make_not_active':
            message = f"""Уважаемый(ая) {partner_name},

Уведомляем Вас, что проект "{project_name}" был приостановлен рекламодателем {advertiser_name}.

Все активные ссылки перестали работать. Вы можете найти другие проекты для продвижения в вашем кабинете."""
            
        elif type_mailing == 'make_active':
            message = f"""Уважаемый(ая) {partner_name},

Рады сообщить, что проект "{project_name}" снова активирован рекламодателем {advertiser_name}!

Теперь вы можете возобновить его продвижение. Все ваши ссылки снова активны."""
            
        elif type_mailing == 'change_price':
            message = f"""Уважаемый(ая) {partner_name},

Уведомляем Вас, что в проекте "{project_name}" рекламодателем {advertiser_name} была изменена цена.

Система временно приостановила проект для обновления условий. Как только изменения будут обработаны, проект снова станет доступен."""
        

        recipients_data.append({
            'email': partner_email,
            'subject': f'Проект "{project_name}" удален рекламодателем',
            'message': message
        })

        try:
            mass_mailing.delay(recipients_data)
        except Exception as mail_error:
            print(f"Ошибка отправки письма: {mail_error}")