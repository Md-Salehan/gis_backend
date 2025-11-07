from rest_framework import serializers

class LegendRequestSerializer(serializers.Serializer):
    layer_ids = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    options = serializers.JSONField(required=False)