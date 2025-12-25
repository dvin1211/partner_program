from datetime import timedelta

from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone

from utils import _paginate,_apply_search


from apps.core.decorators import role_required
from apps.advertisers.forms import ProjectForm,ProjectParamForm
from apps.advertisers.models import Project, AdvertiserActivity
from apps.tracking.models import Conversion, ClickEvent


@role_required('advertiser')
def projects(request):
    """Страница с проектами рекламодателя"""
    user = request.user
    
    notifications_count = AdvertiserActivity.objects.filter(advertiser=user.advertiserprofile,is_read=False).count()
    
    three_days_ago = timezone.now() - timedelta(days=3)
    projects = Project.objects.filter(
        Q(deleted_at__isnull=True) | Q(deleted_at__isnull=False,deleted_at__gte=three_days_ago),advertiser=user
    ).select_related('advertiser').order_by('-created_at')
    
    projects_search_q = request.GET.get('projects_search', '').strip()

    if projects_search_q:
        projects = _apply_search(projects, projects_search_q,['name'])
        
    projects_page = _paginate(request, projects, 6, 'projects_page')
    
    clicks_count = ClickEvent.objects.filter(advertiser=user.advertiserprofile).count()
    conversion_percent = 0
    conversions = Conversion.objects.filter(advertiser=user.advertiserprofile).select_related("project","partner").order_by("-created_at")
    conversions_count = conversions.count()
    if clicks_count > 0:
        conversion_percent =  f"{(conversions_count / clicks_count) * 100:.2f}"
    
    context = {
        "notifications_count":notifications_count,
        
        "projectForm": ProjectForm(),
        'projectParamForm':ProjectParamForm(),
        "projects": projects_page,
        "clicks_count":clicks_count,
        "conversion_percent":conversion_percent,
        "projects_search_query":projects_search_q,
    }
    return render(request, 'advertisers/projects/projects.html',context=context)