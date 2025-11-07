from rest_framework import serializers
from .models import WgtGdPortalMst



class PortalSerializer(serializers.ModelSerializer):
    class Meta:
        model = WgtGdPortalMst
        fields = '__all__'
