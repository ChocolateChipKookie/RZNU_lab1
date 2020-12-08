# Create your views here.
from django.contrib.auth.models import User
from django.http import JsonResponse, QueryDict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework import permissions
from rest_framework import authentication
from django.utils import timezone

from lab_1.rest_api.serializers import ProfileSerializer, PostSerializer
from lab_1.rest_api.models import Profile, Post
import json


# ToDo:
#   Create user manual for follow
#   Test code

class UsersView(APIView):
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        try:
            # List all the profiles in the database
            profiles = ProfileSerializer(Profile.objects.all(), many=True, context={'request': request})
            return Response(profiles.data, status=status.HTTP_200_OK)
        except:
            return JsonResponse({"detail": "Error fetching posts"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    class UserView(APIView):
        authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
        permission_classes = [permissions.AllowAny]
        renderer_classes = [JSONRenderer]

        def get(self, request, username):
            # Get user information
            try:
                # Convert username
                username = username.lower()

                # Check if username exists
                if not User.objects.filter(username=username).exists():
                    return JsonResponse({"detail": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

                # Fetch user and check if there is an linked profile
                user = User.objects.get(username=username)
                if not Profile.objects.filter(user=user).exists():
                    return JsonResponse({"detail": "Cannot check pure user"}, status=status.HTTP_403_FORBIDDEN)

                # Serialize profile and return response
                profile = ProfileSerializer(Profile.objects.get(user=user), context={'request': request})
                return Response(profile.data, status=status.HTTP_200_OK)
            except:
                return JsonResponse({"detail": "Error finding user"}, status=status.HTTP_400_BAD_REQUEST)

        def put(self, request, username):
            """
            Create or update user
            Updateable fields:
            Possible fields
            {
                "username":     "username"
                "password":     "password",
                "email":        "email",
                "first_name":   "name",
                "last_name":    "surname"
                "superuser":    value
            }
            """

            try:
                # Convert data to json
                if isinstance(request.data, QueryDict):
                    data = dict(request.data)
                    for key in data:
                        data[key] = data[key][0]
                else:
                    data = json.loads(request.data.decode("utf-8"))
                # Usernames are stored as lowercase letters
                username = username.lower()

                if request.user.is_authenticated:
                    # Modify user option
                    # Check because the superusers can also modify profiles
                    if not User.objects.filter(username=username).exists():
                        return JsonResponse({"detail": f"User \'{username}\' does not exist!"}, status=status.HTTP_400_BAD_REQUEST)

                    # User exists
                    # Check if superuser or the user to be edited
                    if not (request.user.username.lower() == username or request.user.is_superuser):
                        return JsonResponse({"detail": "Permission denied!"}, status=status.HTTP_403_FORBIDDEN)

                    if len(data) != 1:
                        return JsonResponse({"detail": "Can only modify one option at a time!"}, status=status.HTTP_400_BAD_REQUEST)

                    # Fetch user
                    user = User.objects.get(username=username)

                    # Try modify superuser status
                    if "superuser" in data:
                        # Can only be modified by admin
                        if request.user.username != "admin":
                            return JsonResponse({"detail": "Permission denied!"}, status=status.HTTP_403_FORBIDDEN)
                        # Cannot change admins superuser status
                        if user.name == "admin":
                            return JsonResponse({"detail": "Cannot modify admin superuser status!"}, status=status.HTTP_403_FORBIDDEN)

                        user.is_superuser = data["superuser"]
                        user.save()
                        return JsonResponse({"detail": "Superuser status successfully updated!"}, status=status.HTTP_200_OK)

                    # Try set new username
                    if "username" in data:
                        new_username = data["username"].lower()
                        # Username has to be alphanumeric
                        if any(not c.isalnum() for c in new_username):
                            return JsonResponse({"detail": "Username must be alphanumeric!"}, status=status.HTTP_400_BAD_REQUEST)
                        # Username cannot be a digit
                        if username.isnumeric():
                            return JsonResponse({"detail": "Username cannot be a number!"}, status=status.HTTP_400_BAD_REQUEST)

                        if User.objects.filter(username=new_username).exists():
                            return JsonResponse({"detail": "Account with new username address exists!"}, status=status.HTTP_400_BAD_REQUEST)

                        user.username = new_username
                        user.save()
                        return JsonResponse({"detail": "Username successfully modified!"}, status=status.HTTP_200_OK)

                    # Try set email
                    if "email" in data:
                        new_email = data["email"].lower()
                        if User.objects.filter(email=new_email).exists():
                            return JsonResponse({"detail": "Account with new email address exists!"}, status=status.HTTP_400_BAD_REQUEST)
                        user.email = new_email
                        user.save()
                        return JsonResponse({"detail": "Email successfully modified!"}, status=status.HTTP_200_OK)

                    # Set new password
                    if "password" in data:
                        user.set_password(data["password"])
                        user.save()
                        return JsonResponse({"detail": "Password successfully modified!"}, status=status.HTTP_200_OK)

                    # Set new name
                    if "first_name" in data:
                        user.first_name = data["first_name"]
                        user.save()
                        return JsonResponse({"detail": "First name successfully modified!"}, status=status.HTTP_200_OK)

                    # Set last name
                    if "last_name" in data:
                        user.last_name = data["last_name"]
                        user.save()
                        return JsonResponse({"detail": "Last name successfully modified!"}, status=status.HTTP_200_OK)

                    return JsonResponse({"detail": "User not modified, field does not exist"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Request is not authenticated

                    # Check if has all needed information:
                    for key in ['username', 'password', 'email']:
                        if key not in data:
                            return JsonResponse({"detail": f"Missing new user data: {key}!"}, status=status.HTTP_400_BAD_REQUEST)

                    # Check if usernames are same
                    if username != data['username']:
                        return JsonResponse({"detail": "Usernames in url and json don\'t match!"}, status=status.HTTP_400_BAD_REQUEST)

                    # Username has to be alphanumeric
                    if any(not c.isalnum() for c in username):
                        return JsonResponse({"detail": "Username must be alphanumeric!"}, status=status.HTTP_400_BAD_REQUEST)

                    # Username cannot be a digit
                    if username.isnumeric():
                        return JsonResponse({"detail": "Username cannot be a number!"}, status=status.HTTP_400_BAD_REQUEST)

                    # Create new profile
                    serializer = ProfileSerializer(data={"following": [],"user": data})
                    # Check if data is valid
                    if not serializer.is_valid():
                        return JsonResponse({"detail": "Error creating user profile!"}, status=status.HTTP_400_BAD_REQUEST)
                    # Create user
                    serializer.save()
                    # Return HTTP 201 CREATED signal
                    return JsonResponse({"detail": f"User {username} created!"}, status=status.HTTP_201_CREATED)
            except:
                return JsonResponse({"detail": "Error creating account!"}, status=status.HTTP_400_BAD_REQUEST)

        def delete(self, request, username):
            """
            Delete account
            """
            try:
                # Username can only be lowercase
                username = username.lower()

                # Check if authenticated
                if not request.user.is_authenticated:
                    return JsonResponse({"detail": "Error deleting account, not authenticated!"}, status=status.HTTP_401_UNAUTHORIZED)

                # Check if the user has the permission to delete the user
                # User has permission to delete his own account
                # Superusers have the permission to delete other users
                if not (request.user.username.lower() == username.lower() or request.user.is_superuser):
                    return JsonResponse({"detail": "Error deleting account, access denied!"}, status=status.HTTP_403_FORBIDDEN)

                # Admin cannot be deleted
                if username.lower() == "admin":
                    return JsonResponse({"detail": "Admin user cannot be deleted!"}, status=status.HTTP_403_FORBIDDEN)

                # Check if user exists, maybe superuser had a typo
                if not User.objects.filter(username=username).exists():
                    return JsonResponse({"detail": "Account with given username doesn\'t exist!"}, status=status.HTTP_404_NOT_FOUND)

                # Fetch user
                user = User.objects.get(username=username)

                # Superuser cannot be deleted by anyone but by admin
                if user.is_superuser and request.user.username != "admin":
                    return JsonResponse({"detail": "Superusers can only be deleted by the admin!"}, status=status.HTTP_403_FORBIDDEN)

                # Delete user
                user.delete()
                return JsonResponse({"detail": f"User {username} deleted!"}, status=status.HTTP_200_OK)
            except:
                return JsonResponse({"detail": "Error deleting account!"}, status=status.HTTP_400_BAD_REQUEST)

    class FollowView(APIView):
        authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
        permission_classes = [permissions.IsAuthenticated]

        def put(self, request, username):
            try:
                # Check if authenticated
                if not request.user.is_authenticated:
                    return JsonResponse({"detail": "Request must be authenticated!"}, status=status.HTTP_401_UNAUTHORIZED)

                # Set the username to lowercase
                username = username.lower()
                # Check if trying to follow self
                if username == request.user.username:
                    return JsonResponse({"detail": "Cannot follow yourself!"}, status=status.HTTP_400_BAD_REQUEST)

                # Check if pure user
                if not Profile.objects.filter(user=request.user).exists():
                    return JsonResponse({"detail": "Pure users cannot follow other users!"}, status=status.HTTP_403_FORBIDDEN)

                # Fetch profile
                profile = Profile.objects.get(user=request.user)

                # Check if user exists
                if not User.objects.filter(username=username).exists():
                    return JsonResponse({"detail": "Error following user!"}, status=status.HTTP_400_BAD_REQUEST)
                # Fetch other user
                other_user = User.objects.get(username=username)

                # Check if profile exists
                if not Profile.objects.filter(user=other_user).exists():
                    return JsonResponse({"detail": "Cannot follow pure users!"}, status=status.HTTP_400_BAD_REQUEST)
                # Fetch other profile
                other_profile = Profile.objects.get(user=other_user)

                # Check if already following that user
                if profile.following.filter(user=other_user).exists():
                    return JsonResponse({"detail": "Cannot follow user twice!"}, status=status.HTTP_400_BAD_REQUEST)

                profile.following.add(other_profile)
                profile.save()
                return JsonResponse({"detail": f"Now following {other_user.username}!"}, status=status.HTTP_200_OK)
            except:
                return JsonResponse({"detail": "Error following user!"}, status=status.HTTP_400_BAD_REQUEST)

        def delete(self, request, username):
            try:
                # Check if authenticated
                if not request.user.is_authenticated:
                    return JsonResponse({"detail": "Request must be authenticated!"}, status=status.HTTP_401_UNAUTHORIZED)

                # Set the username to lowercase
                username = username.lower()

                # Check if pure user
                if not Profile.objects.filter(user=request.user).exists():
                    return JsonResponse({"detail": "Pure users cannot unfollow other users!"}, status=status.HTTP_403_FORBIDDEN)

                profile = Profile.objects.get(user=request.user)

                # Check if other user exists
                if not User.objects.filter(username=username).exists():
                    return JsonResponse({"detail": "Cannot unfollow user that you don\'t follow!"}, status=status.HTTP_400_BAD_REQUEST)

                # Fetch other user
                other_user = User.objects.get(username=username)
                if not profile.following.filter(user=other_user).exists():
                    return JsonResponse({"detail": "Cannot unfollow user that you don\'t follow!"}, status=status.HTTP_400_BAD_REQUEST)

                # Fetch other profile
                other_profile = profile.following.get(user=other_user)

                profile.following.remove(other_profile)
                profile.save()
                return JsonResponse({"detail": f"Unfollowed {other_user.username}!"}, status=status.HTTP_200_OK)
            except:
                return JsonResponse({"detail": "Error unfollowing user!"}, status=status.HTTP_400_BAD_REQUEST)


class PostsView(APIView):
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]
    serializer_class = PostSerializer

    def get(self, request):
        try:
            # List all the posts in the database
            posts = self.serializer_class(Post.objects.all(), many=True, context={'request': request})
            return Response(posts.data, status=status.HTTP_200_OK)
        except:
            return JsonResponse({"detail": "Server error!"}, status=status.HTTP_400_BAD_REQUEST)

    class PostView(APIView):
        authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
        permission_classes = [permissions.AllowAny]
        renderer_classes = [JSONRenderer]
        serializer_class = PostSerializer

        def get(self, request, id):
            # Get post
            try:
                # Check if post exists
                if not Post.objects.filter(id=id).exists():
                    return JsonResponse({"detail": "Post doesn\'t exist!"}, status=status.HTTP_404_NOT_FOUND)
                # Get post
                post = Post.objects.get(id=id)
                post = self.serializer_class(post, context={'request': request})
                return Response(post.data, status=status.HTTP_200_OK)
            except:
                return JsonResponse({"detail": "Error finding post!"}, status=status.HTTP_400_BAD_REQUEST)

        def delete(self, request, id):
            # Delete post
            try:
                # Check if authorised
                if not request.user.is_authenticated:
                    return JsonResponse({"detail": "Error deleting post, not authenticated!"}, status=status.HTTP_401_UNAUTHORIZED)

                # Check if post exists
                if not Post.objects.filter(id=id).exists():
                    return JsonResponse({"detail": "Error deleting post, post doesn\'t exist!"}, status=status.HTTP_404_NOT_FOUND)

                # Fetch post, profile and user
                post = Post.objects.get(id=id)
                profile = post.profile
                user = profile.user
                # Check if has permission to delete
                if request.user.username == user.username or request.user.is_superuser:
                    # Delete user
                    post.delete()
                    return JsonResponse({"detail": f"Post {id} deleted!"}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"detail": "Permission denied!"}, status=status.HTTP_403_FORBIDDEN)

            except:
                return JsonResponse({"detail": "Error deleting post!"}, status=status.HTTP_400_BAD_REQUEST)

    class UserPostsView(APIView):
        authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
        permission_classes = [permissions.AllowAny]
        renderer_classes = [JSONRenderer]
        serializer_class = PostSerializer

        def get(self, request, username):
            # Get posts by user
            try:
                # Transform username
                username = username.lower()
                # Check if user exists
                if not User.objects.filter(username=username).exists():
                    return JsonResponse({"detail": "User does not exist!"}, status=status.HTTP_404_NOT_FOUND)
                # Fetch user
                user = User.objects.get(username=username)
                # Check if profile exists
                if not Profile.objects.filter(user=user).exists():
                    return JsonResponse({"detail": "User profile does not exist!"}, status=status.HTTP_404_NOT_FOUND)
                # Get profile
                profile = Profile.objects.get(user=user)
                # Get posts
                posts = profile.get_posts()
                posts_serialized = self.serializer_class(posts, many=True, context={'request': request})
                return Response(posts_serialized.data, status=status.HTTP_200_OK)
            except:
                return JsonResponse({"detail": "Error finding post!"}, status=status.HTTP_400_BAD_REQUEST)

    class NewPostView(APIView):
        authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
        permission_classes = [permissions.IsAuthenticated]
        renderer_classes = [JSONRenderer]

        def post(self, request):
            try:
                # Check if content is short enough
                if len(request.body) > 256:
                    return JsonResponse({"detail": f"Post too long ({len(request.body)}), maximum length is 256 bytes"}, status=status.HTTP_400_BAD_REQUEST)
                # Decode content
                content = request.body.decode('utf-8')
                # Get time of creation
                created = timezone.now()

                if not Profile.objects.filter(user=request.user).exists():
                    return JsonResponse({"detail": "Profile does not exist! Pure user cannot create posts"}, status=status.HTTP_400_BAD_REQUEST)

                profile = Profile.objects.get(user=request.user)
                post = Post.objects.create(content=content, created=created, profile=profile)
                return JsonResponse({"detail": f"Post {post.id} created"}, status=status.HTTP_201_CREATED)
            except:
                return JsonResponse({"detail": "Error posting!"}, status=status.HTTP_400_BAD_REQUEST)

