from rest_framework import serializers

from django.contrib.auth import get_user_model

from user.models import Messages


class MsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = "__all__"

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True}
        }
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
