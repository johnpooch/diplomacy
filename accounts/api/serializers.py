from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

User._meta.get_field('email')._unique = True


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        return user

    def validate_password(self, password):
        email = self.initial_data.get('email')
        username = self.initial_data.get('username')
        temp_user = User(email=email, username=username)
        validate_password(password, temp_user)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError(
            'The username or password you entered do not match an account. '
            'Please try again.'
        )


class ChangePasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(
        write_only=True,
        required=True,
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'current_password',
            'new_password',
            'new_password_confirm'
        )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Password fields didn\'t match'}
            )
        return attrs

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not user.check_password(current_password):
            raise serializers.ValidationError('Password is not correct')
        return current_password

    def validate_new_password(self, new_password):
        validate_password(new_password)
        return new_password

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
