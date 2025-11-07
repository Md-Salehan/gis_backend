from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer


# Import models
from .models import WgtGdLayerMst, WgtGdPortalLayerMap, Feature



class LayerMstSerializer(serializers.ModelSerializer):
    class Meta:
        model = WgtGdLayerMst
        fields = '__all__'


class PortalLayerMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = WgtGdPortalLayerMap
        fields = '__all__'

class PortalLayersRequestSerializer(serializers.Serializer):
    portal_id = serializers.CharField(max_length=5, required=True)
    
    def validate_portal_id(self, value):
        """Validate portal_id format"""
        if not value.strip():
            raise serializers.ValidationError("portal_id cannot be empty")
        if len(value) > 5:
            raise serializers.ValidationError("portal_id cannot exceed 5 characters")
        return value.strip()
    



class FeatureSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Feature
        geo_field = 'geometry'
        fields = ('id', 'name', 'description')