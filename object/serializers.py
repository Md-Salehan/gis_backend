from rest_framework import serializers

# Import models
from .models import WgtGdObjMst



class ObjMstSerializer(serializers.ModelSerializer):
    class Meta:
        model = WgtGdObjMst
        fields = '__all__'



class LayerObjectRequestSerializer(serializers.Serializer):
    layer_id = serializers.CharField(max_length=5, required=True)

    def validate_layer_id(self, value):
        if not value.strip():
            raise serializers.ValidationError("layer_id cannot be empty")
        if len(value) > 5:
            raise serializers.ValidationError("layer_id cannot exceed 5 characters")
        return value.strip()