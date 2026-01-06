from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from apps.core.decorators import role_required
from apps.partners.models import PartnerLink

@role_required('partner')
@require_POST
def delete_partner_link(request, link_id):
    partner_link = get_object_or_404(PartnerLink,id=link_id,partner=request.user)
    partner_link.delete()
    messages.success(request,message="Партнёрская ссылка успешно удалена!",extra_tags="delete_link_success")
    return redirect('partner_links')