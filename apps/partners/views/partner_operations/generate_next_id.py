from django.db import connection
from django.http import JsonResponse

from django.views.decorators.http import require_POST


@require_POST
def generate_next_link_id(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT nextval('partners_partnerlink_id_seq')")
        return JsonResponse({"success": True, "partner_link_id": int(cursor.fetchone()[0])})
    