from django.contrib.auth.models import User, Group
from lab_1.rest_api.models import *
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'id', 'url', 'email', 'password', 'first_name', 'last_name', 'date_joined')
        extra_kwargs = {
            'url': {'view_name': 'user-detail', 'lookup_field': 'username'},
        }

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"].lower()).exists():
            raise serializers.ValidationError("User with same e-mail address exists")
        if User.objects.filter(username=attrs["username"].lower()).exists():
            raise serializers.ValidationError("User with same username address exists")
        return attrs

    def create(self, validated_data):
        # Only lowercase letters allowerd in username
        user = User.objects.create(
            username=validated_data["username"].lower(),
            password=validated_data["password"],
            email=validated_data["email"].lower()
        )

        if "first_name" in validated_data:
            user.first_name = validated_data["first_name"]
            user.save()
        if "surname" in validated_data:
            user.last_name = validated_data["last_name"]
            user.save()

        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        try:
            user.set_password(validated_data['password'])
            user.save()
        except KeyError:
            pass
        return user


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    following = UserSerializer(required=True, many=True)

    class Meta:
        model=Profile
        fields = ('following', 'user')


    def create(self, validated_data):
        serializer = UserSerializer()
        user = serializer.create(validated_data['user'])
        profile = Profile.objects.create(user=user)
        return profile





class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ['content', 'created', 'profile']