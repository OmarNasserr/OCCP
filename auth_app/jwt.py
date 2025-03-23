from tokenize import TokenError

from rest_framework_simplejwt.serializers import (
    TokenObtainSerializer,
    TokenBlacklistSerializer
)
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate, get_user_model
from rest_framework.exceptions import AuthenticationFailed
User = get_user_model()


#################################################################
# Custom Token Obtain Pair Serializer, to make it work add it in the SIMPLE_JWT settings in the settings.py
#################################################################

class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the default required flags for username and password
        if self.username_field in self.fields:
            self.fields[self.username_field].required = False
        if 'password' in self.fields:
            self.fields['password'].required = False

    # override the get_token function in order to add a token_version in the encryption to avoid using blacklisting mechanism
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add token_version to jwt token
        token['token_version'] = user.token_version
        return token

    """
        This acts as the login function
    """
    def validate(self, attrs):

        request = self.context.get('request')

        user = None
        if 'username' in request.data and 'password' in request.data:
            user = authenticate(
                request=self.context['request'],
                username=attrs[self.username_field],
                password=attrs["password"],
            )

        if not user:
            self._raise_authentication_error('Login Failed.')


        refresh = self.get_token(user)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return {
            'message': 'Login Successful.',
            'username': user.username,
            'token': {
                'refresh': data["refresh"],
                'access': data["access"]
            },
        }

    def _raise_authentication_error(self, message):
        """Helper method to raise an AuthenticationFailed exception."""
        raise AuthenticationFailed({
            'message': message,
            'status': 401,
        })

class CustomTokenBlacklistSerializer(TokenBlacklistSerializer):
    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])
        try:
            refresh.blacklist()
        except AttributeError:
            pass
        return {
            "message": "Logout Successful",
            "status_code": 200
        }

class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs):
        try:
            refresh = self.token_class(attrs['refresh'])
            data = {
                'access': str(refresh.access_token),
            }

            if api_settings.ROTATE_REFRESH_TOKENS:
                if api_settings.BLACKLIST_AFTER_ROTATION:
                    try:
                        refresh.blacklist()
                    except AttributeError:
                        pass  # Blacklist app not installed

                refresh.set_jti()
                refresh.set_exp()
                refresh.set_iat()

                data['refresh'] = str(refresh)

            return data

        except TokenError as e:
            return {
                "message": f'{e}',
                "status": 400,
            }
