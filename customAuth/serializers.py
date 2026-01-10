from rest_framework import serializers



class LoginSerializer(serializers.Serializer):
    userId = serializers.CharField()
    password = serializers.CharField()
    ipAddress = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    appLogNo = serializers.CharField(max_length=20)