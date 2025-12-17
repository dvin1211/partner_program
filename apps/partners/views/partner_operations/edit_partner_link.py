from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from apps.partners.models import PartnerLink

@login_required
@require_POST
def edit_link(request, link_id):
    partner_link = get_object_or_404(PartnerLink,id=link_id,partner=request.user)
    partner_link.url = request.POST['newGeneratedLink']
    partner_link.save()
    messages.success(request,message="Партнёрская ссылка успешно изменена!",extra_tags="edit_link_success")
    return redirect('partner_links')