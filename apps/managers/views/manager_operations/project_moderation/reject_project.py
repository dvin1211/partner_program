from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.core.decorators import role_required
from apps.advertisers.models import Project, AdvertiserActivity
from utils import send_email_via_mailru


@role_required('manager')
@require_POST
def reject_project(request, project_id):
    project = get_object_or_404(Project,id=project_id)
    reason = request.POST.get('moderation_rejection_reason')
    if project.new_cost_per_action and project.new_cost_per_action != project.cost_per_action:
        project.status = 'Подтверждено'
        project.new_cost_per_action = project.cost_per_action
        project.save()
        AdvertiserActivity.objects.create(
        advertiser=project.advertiser.advertiserprofile,
        activity_type='reject',
        title='Изменение цены было отклонено',
        details=f'Цена за действие в проекте {project.name} установлена прежней. Причина: {reason}'
    )
        if project.advertiser.email_notifications:
            try:
                send_email_via_mailru.delay(project.advertiser.email,f"Цена за действие в проекте {project.name} установлена прежней по причине: {reason}",
                                       'Уведомление об отклонении в изменении цены за действие в проекте')
            except:
                pass
        messages.success(request,message=f"Цена за действие у проекта {project.name} была установлена прежней",extra_tags="reject_success")
        return redirect("manager_projects")
        
    project.status = 'Отклонено'
    project.is_active = False
    project.save()
    if project.advertiser.email_notifications:
        try:
            send_email_via_mailru.delay(project.advertiser.email,f"Проект {project.name} был отклонен модератором по причине: {reason}", 'Уведомление об отклонении проекта')
        except:
            pass
    
    AdvertiserActivity.objects.create(
        advertiser=project.advertiser.advertiserprofile,
        activity_type='reject',
        title='Проект отклонен',
        details=f'{project.name} был отклонен модератором. Причина: {reason}'
    )
    messages.success(request,message=f"Проект {project.name} был отклонен",extra_tags="reject_success")
    return redirect("manager_projects")
