from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.advertisers.models import Project
from apps.core.decorators import role_required
from apps.partnerships.models import ProjectPartner
from utils import mass_mailing


@role_required('advertiser')
@require_POST
def delete_project(request, project_id):
    """
    Удаление проекта с уведомлением партнеров
    """
    try:
        # Начинаем транзакцию
        with transaction.atomic():
            # Получаем проект внутри транзакции
            project = get_object_or_404(
                Project, 
                id=project_id, 
                advertiser=request.user
            )
            
            project_name = project.name
            project_id_str = str(project_id)
            advertiser_name = request.user.username
            
            partnerships = ProjectPartner.objects.filter(
                project=project
            ).select_related('partner')
            
            
            recipients_data = []
            
            for partnership in partnerships:
                partner_email = partnership.partner.email
                partner_name = partnership.partner.username
                
                # Создаем персонализированное сообщение
                message = f"""Уважаемый(ая) {partner_name},

Уведомляем Вас, что проект "{project_name}" (ID: {project_id_str}) 
был удален рекламодателем "{advertiser_name}" из нашей платформы."""
                
                recipients_data.append({
                    'email': partner_email,
                    'subject': f'Проект "{project_name}" удален рекламодателем',
                    'message': message
                })
            
            project.soft_delete()
        
        for recipient_data in recipients_data:
            try:
                mass_mailing.delay(
                    mass_mailing=recipient_data['email'],
                    message=recipient_data['message'],
                    subject=recipient_data['subject']
                )
            except Exception as mail_error:
                # Логируем ошибку отправки, но не прерываем выполнение
                print(f"Ошибка отправки письма {recipient_data['email']}: {mail_error}")
                # Можно сохранить в лог или отправить уведомление админу
        
        messages.success(
            request, 
            f"Проект '{project_name}' успешно удален. Уведомления отправлены {len(recipients_data)} партнерам.",
            extra_tags="project_delete_success"
        )
        
    except Project.DoesNotExist:
        messages.error(
            request, 
            "Проект не найден или у вас нет прав на его удаление.",
            extra_tags="project_delete_error"
        )
    except Exception as e:
        # Транзакция автоматически откатится при исключении
        messages.error(
            request, 
            f"Произошла ошибка при удалении проекта: {str(e)}",
            extra_tags="project_delete_error"
        )
    return redirect("advertiser_projects")


