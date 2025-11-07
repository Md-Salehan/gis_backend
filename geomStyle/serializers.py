from rest_framework import serializers
from .models import WgtGdGeomStyleMst



class GeomStyleMstSerializer(serializers.ModelSerializer):
    class Meta:
        model = WgtGdGeomStyleMst
        fields = '__all__'
