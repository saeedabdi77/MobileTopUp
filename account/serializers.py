from rest_framework.serializers import ModelSerializer
from account.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class SignUpSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    repeat_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'repeat_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['repeat_password']:
            raise serializers.ValidationError({"password": ""})

        return attrs

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']

        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()

        return user
