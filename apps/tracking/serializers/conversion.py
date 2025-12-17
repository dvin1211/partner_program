from rest_framework import serializers
from apps.tracking.models import Conversion

class ConversionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversion
        fields = ["project", "partner","advertiser", "amount", "details","partner_link","platform","partnership","referrer","user_agent","ip_address"]