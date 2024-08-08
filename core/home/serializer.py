from rest_framework import serializers
from .models import Image, CustomUser

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        if CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError('Username is taken.')
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError('User already exists.')
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create(username=validated_data['username'], email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()




class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'date_joined', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class SelectedPhotoSerializer(serializers.Serializer):
    query=serializers.CharField()
    photo_url=serializers.URLField()
    photographer=serializers.CharField()