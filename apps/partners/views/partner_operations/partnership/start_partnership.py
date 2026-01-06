from django.shortcuts import redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.advertisers.models import Project
from apps.core.decorators import role_required
from apps.partnerships.models import ProjectPartner
from utils import send_email_via_mailru

@role_required('partner')
@require_POST
def connect_project(request, project_id):
    """Подключиться к проекту рекламодателя"""
    project = get_object_or_404(Project,id=project_id)
    partner = request.user
    
    if not hasattr(partner,"partner_profile"):
        return redirect('index')
    
    if ProjectPartner.objects.filter(project=project, partner=partner).exists():
        messages.warning(request, message='Вы уже подключены к этому проекту',extra_tags="already_connected_project")
        return redirect('partner_offers')
        
    
    send_email_via_mailru.delay(project.advertiser.email,f"К проекту {project.name} подключился партнёр {partner.get_full_name()} {partner.email}","Новый партнёр")
    
    ProjectPartner.objects.create(
        project=project,
        partner=partner,
        advertiser=project.advertiser
    )
    messages.success(request,message="Вы успешно подключились к проекту рекламодателя",extra_tags="connect_project_success")
    return redirect("partner_offers")