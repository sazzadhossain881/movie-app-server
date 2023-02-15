"""serializer for the user api view"""

from rest_framework import serializers
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    """serializer for the user object"""
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
            }
        }

    def create(self, valdated_data):
        """create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**valdated_data)

    def update(self, instance, validated_data):
        """update and return user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('unable to authenticate with provided credential')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs
