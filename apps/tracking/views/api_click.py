from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.users.models import User
from apps.partners.models import Platform,PartnerProfile,PartnerLink
from apps.advertisers.models import AdvertiserProfile,Project
from apps.partnerships.models import ProjectPartner
from apps.tracking.serializers import ClickSerializer

class ClickAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        partner_id = request.data.get("partner")
        partner_link_id = request.POST.get('pid')
        project_id = request.data.get("project")
        referrer_id = request.data.get('referrer')

        if partner_id is None:
            return Response(
                {"detail": "Параметр 'partner' обязателен. Пожалуйста, укажите ID партнера."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if project_id is None:
            return Response(
                {"detail": "Параметр 'project' обязателен. Пожалуйста, укажите ID проекта."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            partner = User.objects.get(id=int(partner_id))
            partnerprofile = PartnerProfile.objects.get(
                user=int(partner.id)
            )
        except User.DoesNotExist:
            return Response({
                "error": "Партнёр с указанным ID не найден. Пожалуйста, проверьте правильность введенного ID."
            }, status=status.HTTP_404_NOT_FOUND)
        try:
            partnership = ProjectPartner.objects.get(
                partner=partner_id,
                project=project_id
            )
            project = Project.objects.get(
                id=project_id
            )
        except ProjectPartner.DoesNotExist:
            return Response(
                {"detail": "Нет такого проекта или партнёр не сотрудничает с ним!"},
                status=status.HTTP_404_NOT_FOUND
            )
        if partner.is_currently_blocked():
            return Response(
                {"detail": "Сотрудничество с данным партнёром приостановлено, т.к. аккаунт партнёра заблокирован!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not project.is_active:
            return Response(
                {"detail": "На данный момент проект неактивен!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if project.status == project.StatusType.DELETED:
            return Response(
                {"detail": "Сотрудничество остановлено, т.к. проект рекламодателя был удален!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif project.status == project.StatusType.BLOCKED:
            return Response(
                {"detail": "Сотрудничество остановлено, т.к. проект рекламодателя заблокирован!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if partnership.status != partnership.StatusType.ACTIVE:
            return Response(
                {"detail": "Сотрудничество с данным партнёром на данный момент приостановлено!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        advertiser = User.objects.get(id=partnership.project.advertiser.id)
        adv_profile = AdvertiserProfile.objects.get(
            user=int(advertiser.id)
        )
        if advertiser.is_currently_blocked():
            return Response(
                {"detail": "Сотрудничество с данным рекламодателем приостановлено, т.к. аккаунт рекламодателя заблокирован!"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if partnership.partner_links.count() < 1:
            return Response({"detail":"Переход не может быть засчитан, т.к. не сгенерирована партнёрская ссылка!"},status=status.HTTP_400_BAD_REQUEST)
        
        partner_link = None
        try:
            partner_link = PartnerLink.objects.get(id=partner_link_id)
            if partner_link.project != project:
                return Response({"detail":"Переход не может быть засчитан, т.к. не ссылка не принадлежит данному проекту!"},status=status.HTTP_400_BAD_REQUEST)
        except PartnerLink.DoesNotExist:
            return Response({"detail":"Переход не может быть засчитан, т.к. не найдена партнёрская ссылка с таким id!"},status=status.HTTP_400_BAD_REQUEST)
        
        if referrer_id:
            try:
                platform = Platform.objects.get(
                    id=referrer_id,
                    is_active=True,
                    status=Platform.StatusType.APPROVED
                )
                platform_id = platform.id
                referrer = platform.url_or_id
            except Exception:
                referrer = request.META.get('HTTP_REFERER', '')
                platform_id = None
        else:
            referrer = request.META.get('HTTP_REFERER', '')
            platform_id = None
        
        ip = request.META.get('HTTP_X_FORWARDED_FOR',None)
        if ip:
            ip = ip.split(',')[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        data = {
            "project":request.data["project"],
            "partner":partnerprofile.id,
            "advertiser":adv_profile.id,
            "platform":platform_id,
            "partner_link":partner_link.id,
            "partnership":partnership.id,
            "referrer":referrer,
            "user_agent":request.META.get('HTTP_USER_AGENT', None),
            "ip_address":ip,
        }
        serializer = ClickSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)