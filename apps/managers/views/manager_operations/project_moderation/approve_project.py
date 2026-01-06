from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.core.decorators import role_required
from apps.advertisers.models import Project, AdvertiserActivity
from utils import send_email_via_mailru



@role_required('manager')
@require_POST
def approve_project(request, project_id):
    project = get_object_or_404(Project,id=project_id)
    project.status = 'Подтверждено'
    if project.new_cost_per_action and project.new_cost_per_action != project.cost_per_action:
        project.cost_per_action = project.new_cost_per_action
        project.save()
        AdvertiserActivity.objects.create(
        advertiser=project.advertiser.advertiserprofile,
        activity_type='approve',
        title='Изменение цены было одобрено',
        details=f'Цена за действие в {project.name} была изменена.'
    )
        if project.advertiser.email_notifications:
            try:
                send_email_via_mailru.delay(project.advertiser.email,f"Цена за действие в проекте {project.name} была изменена",
                                        'Уведомление об одобрении в изменении цены за действие в проекте')
            except:
                pass
        messages.success(request,message=f"Цена за действие в проекте {project.name} была измена",extra_tags="approve_success")
        return redirect("manager_projects")
    
    project.save()
    if project.advertiser.email_notifications:
        try:
            send_email_via_mailru.delay(project.advertiser.email,f"Поздравляем, проект {project.name} был одобрен модератором.",'Уведомление о подтвеждении проекта')
        except:
            pass
    
    AdvertiserActivity.objects.create(
        advertiser=project.advertiser.advertiserprofile,
        activity_type='approve',
        title='Проект одобрен',
        details=f'{project.name} был одобрен модератором'
    )
    messages.success(request,message=f"Проект {project.name} был одобрен",extra_tags="approve_success")
    return redirect("manager_projects")