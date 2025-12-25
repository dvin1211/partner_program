from django.shortcuts import render
from django.db.models import Q

from apps.advertisers.models import Project
from apps.core.decorators import role_required
from apps.managers.models import ManagerActivity
from utils import _paginate


@role_required('manager')
def manager_projects(request):  
    """Модерация проектов"""
    user = request.user
    
    projects_search_q = request.GET.get('projects_search','').strip()
    
    count = 10
    
    projects = Project.objects.filter(status='На модерации')
    
    if projects_search_q:
        projects = projects.filter(
            Q(name__icontains=projects_search_q) 
        )
    
    projects = _paginate(request, projects, count, "projects_page")

    notifications_count = ManagerActivity.objects.filter(manager=user.managerprofile,is_read=False).count()
    
    context = {
        "user": user,  
        "projects":projects,
        "notifications_count":notifications_count,
        
        "projects_search_q":projects_search_q
    }
    
    return render(request, 'managers/projects/projects.html',context=context)


