from django.dispatch import receiver, Signal

from apps.partners.models import PartnerActivity
from apps.advertisers.models import AdvertiserActivity

create_activities_signal = Signal()

@receiver(create_activities_signal)
def create_activities(sender, **kwargs):
    partner = kwargs.get('partner')
    advertiser = kwargs.get('advertiser')
    activity_type = kwargs.get('activity_type')
    title = kwargs.get('title')
    partner_details = kwargs.get('partner_details')
    advertiser_details = kwargs.get('advertiser_details')
    PartnerActivity.objects.create(
        partner=partner,
        activity_type=activity_type,
        title=title,
        details=partner_details
    )

    AdvertiserActivity.objects.create(
        advertiser=advertiser,
        activity_type=activity_type,
        title=title,
        details=advertiser_details
    )