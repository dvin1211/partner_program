from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from apps.core.decorators import role_required
from apps.partners.models import PartnerLink

@role_required('partner')
@require_POST
def edit_link(request, link_id):
    partner_link = get_object_or_404(PartnerLink,id=link_id,partner=request.user)
    partner_link.url = request.POST['newGeneratedLink']
    partner_link.save()
    messages.success(request,message="Партнёрская ссылка успешно изменена!",extra_tags="edit_link_success")
    return redirect('partner_links')