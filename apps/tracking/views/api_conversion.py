from decimal import Decimal

from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.users.models import User
from apps.partners.models import Platform,PartnerProfile, PartnerLink
from apps.advertisers.models import AdvertiserProfile,Project
from apps.partnerships.models import ProjectPartner
from apps.tracking.serializers import ConversionSerializer
from apps.tracking.signals import create_activities_signal
from apps.tracking.models import Conversion


class ConversionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        partner_id = request.data.get("partner")
        partner_link_id = request.POST.get('pid')
        project_id = request.data.get("project")
        referrer_id = request.data.get('referrer')

        if partner_link_id is None:
            return Response(
                {"detail": "Параметр 'pid' обязателен для зачисления конверсии. Пожалуйста, укажите ID ссылки."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if partner_id is None:
            return Response(
                {"detail": "Параметр 'partner' обязателен для зачисления конверсии. Пожалуйста, укажите ID партнера."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if project_id is None:
            return Response(
                {"detail": "Параметр 'project' обязателен для зачисления конверсии. Пожалуйста, укажите ID проекта."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            partner = User.objects.get(id=int(partner_id))
            partnerprofile = PartnerProfile.objects.get(
                user=int(partner.id)
            )
        except (User.DoesNotExist,PartnerProfile.DoesNotExist):
            return Response({
                "error": "Партнёр с указанным ID не найден. Пожалуйста, проверьте правильность введенного ID."
            }, status=status.HTTP_404_NOT_FOUND)
        if partner.is_currently_blocked():
            return Response(
                {"detail": "Сотрудничество с данным партнёром на данный момент приостановлено, т.к. аккаунт партнёра заблокирован!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        platform_id = None
        referrer = request.META.get('HTTP_REFERER', '')
        if referrer_id:
            try:
                platform = Platform.objects.get(
                    id=referrer_id,
                    is_active=True,
                    status=Platform.StatusType.APPROVED
                )
                platform_id = platform.id
                referrer = platform.url_or_id
            except Platform.DoesNotExist:
                pass
            
        try:
            partnership = ProjectPartner.objects.get(
                partner=request.data["partner"],
                project=request.data["project"]
            )
            project = Project.objects.get(
                id=request.data['project']
            )
        except ProjectPartner.DoesNotExist:
            return Response(
                {"detail": "Нет такого проекта или партнёр не сотрудничает с ним!"},
                status=status.HTTP_404_NOT_FOUND
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
        details = ""
        if 'details' in request.data:
            details = request.data["details"]
        if not partnership:
            return Response({"detail":"Нет такого проекта или партнёр не сотрудничает с ним!"},status=status.HTTP_400_BAD_REQUEST)
        
        if partnership.partner_links.count() < 1:
            return Response({"detail":"Конверсия не может быть засчитана, т.к. не сгенерирована партнёрская ссылка!"},status=status.HTTP_400_BAD_REQUEST)
        
        partner_link = None
        try:
            partner_link = PartnerLink.objects.get(id=partner_link_id)
            if partner_link.project != project:
                return Response({"detail":"Переход не может быть засчитан, т.к. не ссылка не принадлежит данному проекту!"},status=status.HTTP_400_BAD_REQUEST)
        except PartnerLink.DoesNotExist:
            return Response({"detail":"Переход не может быть засчитан, т.к. не найдена партнёрская ссылка с таким id!"},status=status.HTTP_400_BAD_REQUEST)
        
        ip = request.META.get('HTTP_X_FORWARDED_FOR',None)
        if ip:
            ip = ip.split(',')[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
            
        amount = project.cost_per_action
        if 'amount' in request.data and request.data['amount'].isdigit():
            if float(request.data['amount']) >= project.get_reduced_price:
                amount = request.data['amount']
        data = {
            "project":request.data["project"],
            "partner":partnerprofile.id,
            "advertiser":adv_profile.id,
            "amount":amount,
            "details":details,
            "partner_link":partner_link.id,
            "partnership":partnership.id,
            "platform":platform_id,
            "referrer":referrer,
            "user_agent":request.META.get('HTTP_USER_AGENT', None),
            "ip_address":ip,
            
        }
        serializer = ConversionSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            
            partnership.advertiser.advertiserprofile.balance -= Decimal(amount)
            partnership.partner.partner_profile.balance += Decimal(amount)
            partnership.advertiser.advertiserprofile.save()
            partnership.partner.partner_profile.save()
            
            if 'details' in request.data:
                title = request.data["details"]
            else:
                title = f'Новая продажа. Проект: {partnership.project.name}'
            
            create_activities_signal.send(
                sender=Conversion.__class__,
                partner=partnerprofile,
                advertiser=adv_profile,
                activity_type='sale',
                title=title,
                partner_details = f'Комиссия: {amount} ₽',
                advertiser_details = f'Комиссия: {amount} ₽. Партнёр: {partner.username}'
            )
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)