from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)
