from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self, validated_data):
        account = User(
            username=validated_data.get('username'),
        )
        account.set_password(validated_data['password'])
        account.save()

        return account
