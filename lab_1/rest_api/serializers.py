from lab_1.rest_api.models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'id', 'email', 'password', 'first_name', 'last_name', 'date_joined')

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
        if "last_name" in validated_data:
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
    following_no = serializers.IntegerField(source='get_following_count')
    following = serializers.HyperlinkedRelatedField(view_name='user-detail', lookup_field="username", read_only=True, many=True, source="get_following")

    followers_no = serializers.IntegerField(source='get_followers_count')
    followers = serializers.HyperlinkedRelatedField(view_name='user-detail', lookup_field="username", read_only=True, many=True, source="get_followers")


    url = serializers.HyperlinkedRelatedField(view_name='user-detail', lookup_field='username', source='user', read_only=True)
    follow_url = serializers.HyperlinkedRelatedField(view_name='follow', lookup_field='username', source='user', read_only=True)

    posts = serializers.IntegerField(source='get_posts_count')
    posts_url = serializers.HyperlinkedRelatedField(view_name='posts-user-list', lookup_field='username', source='user', read_only=True)


    class Meta:
        model=Profile
        fields = ('url', 'follow_url', 'user', 'following', 'following_no', 'followers', 'followers_no', 'posts', 'posts_url')

    def create(self, validated_data):
        serializer = UserSerializer()
        user = serializer.create(validated_data['user'])
        profile = Profile.objects.create(user=user)
        return profile


class PostSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(source='profile.user.username', read_only=True)
    user_url = serializers.HyperlinkedRelatedField(view_name="user-detail", read_only=True, lookup_field='username', source='profile.user')
    post_url = serializers.HyperlinkedIdentityField(view_name="post-detail", read_only=True, lookup_field="id")

    class Meta:
        model = Post
        fields = ['content', 'id', 'created', 'created_by', 'post_url', 'user_url']
