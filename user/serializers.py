from rest_framework import serializers
from patient.utils import get_role as get_real_role
from django.contrib.auth import get_user_model

from user.models import Messages, Task


class MsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = "__all__"

class StaffSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True}
        }


    def get_role(self,obj):
        return get_real_role(obj)


    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    assigned_by_name = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = "__all__"
    
    def get_assigned_to_name(self,obj):
        if obj.assigned_to:
            return obj.assigned_to.username
        return None
    
    def get_assigned_by_name(self,obj):
        if obj.assigned_by:
            return obj.assigned_by.username
        return None
