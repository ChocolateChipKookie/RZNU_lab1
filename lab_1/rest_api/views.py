# Create your views here.
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework import permissions
from rest_framework import authentication


from lab_1.rest_api.serializers import ProfileSerializer
from lab_1.rest_api.models import Profile
import json


class TestView(APIView):

    def get(self, request, *args, **kwargs):
        print(request)
        return HttpResponse('Hello, World!')


class UsersView(APIView):
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]
    serializer_class = ProfileSerializer

    def get(self, request):
        # List all the profiles in the database
        profiles = self.serializer_class(Profile.objects.all(), many=True, context={'request': request})
        return Response(profiles.data, status=status.HTTP_200_OK)

    class UserView(APIView):
        authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
        permission_classes = [permissions.AllowAny]
        renderer_classes = [JSONRenderer]
        serializer_class = ProfileSerializer

        def get(self, request, username):
            """
                Get user information
                Check if user exists:
                    Check if profile is connected to user (for example admin doesn't have profile)
                        return data
                return 404
            """

            username = username.lower()

            if User.objects.filter(username=username).exists():
                user_id = User.objects.get(username=username).id
                if Profile.objects.filter(user_id=user_id).exists():
                    profile = self.serializer_class(Profile.objects.get(user_id=user_id), context={'request': request})
                    return Response(profile.data, status=status.HTTP_200_OK)

            return HttpResponse("User does not exist!", status.HTTP_404_NOT_FOUND)

        def put(self, request, username):
            """
            Possible fields
            {
                "username":     "username"
                "password":     "password",
                "email":        "email",
                "first_name":   "name",
                "last_name":    "surname"
                "superuser":    value
            }

            Check if authenticated:
            Authenticated:
                Check if user exists:
                    Check if the user has permission to change options
                        Check if number of options == 1
                            Modify user
            Not authenticated:
                Create new profile with given options
            """

            try:
                # Convert data to json
                data = json.loads(request.body.decode('utf-8'))

                # Usernames are stored as lowercase letters
                username = username.lower()

                if request.user.is_authenticated:
                    # Modify user option
                    # Check because the superusers can also modify profiles
                    if User.objects.filter(username=username).exists():
                        # User exists
                        # Check if superuser or the user to be edited
                        if request.user.username.lower() == username or request.user.is_superuser:
                            # Fetch user
                            user = User.objects.get(username=username)

                            if len(data) != 1:
                                return HttpResponse("Can only modify one option at a time!", status=status.HTTP_400_BAD_REQUEST, content_type="text/plain")

                            # Try modify superuser status
                            if "superuser" in data:
                                # Can only be modified by admin
                                if request.user.username == "admin":
                                    # Cannot change admins superuser status
                                    if user.name != "admin":
                                        user.is_superuser = data["superuser"]
                                        user.save()
                                        return HttpResponse("Superuser status successfully updated!", status=status.HTTP_200_OK, content_type="text/plain")
                                    else:
                                        return HttpResponse("Cannot modify admin superuser status!", status=status.HTTP_400_BAD_REQUEST, content_type="text/plain")
                                else:
                                    return HttpResponse("Permission denied!", status=status.HTTP_403_FORBIDDEN, content_type="text/plain")

                            # Try set new username
                            if "username" in data:
                                new_username = data["username"].lower()

                                if User.objects.filter(username=new_username).exists():
                                    return HttpResponse("Account with new username address exists!", status=status.HTTP_400_BAD_REQUEST, content_type="text/plain")
                                else:
                                    user.username = new_username
                                    user.save()
                                    return HttpResponse("Username successfully modified!", status=status.HTTP_200_OK, content_type="text/plain")

                            # Try set email
                            if "email" in data:
                                new_email = data["email"].lower()
                                if User.objects.filter(email=new_email).exists():
                                    return HttpResponse("Account with new email address exists!", status=status.HTTP_400_BAD_REQUEST, content_type="text/plain")
                                else:
                                    user.email = new_email
                                    user.save()
                                    return HttpResponse("Email successfully modified!", status=status.HTTP_200_OK, content_type="text/plain")

                            # Set new password
                            if "password" in data:
                                user.set_password(data["password"])
                                user.save()
                                return HttpResponse("Password successfully modified!", status=status.HTTP_200_OK, content_type="text/plain")

                            # Set new name
                            if "first_name" in data:
                                user.first_name = data["first_name"]
                                user.save()
                                return HttpResponse("First name successfully modified!", status=status.HTTP_200_OK, content_type="text/plain")

                            # Set last name
                            if "last_name" in data:
                                user.last_name = data["last_name"]
                                user.save()
                                return HttpResponse("Last name successfully modified!", status=status.HTTP_200_OK, content_type="text/plain")

                            return HttpResponse("User not modified, field does not exist", status=status.HTTP_400_BAD_REQUEST, content_type="text/plain")
                        else:
                            return HttpResponse("Permission denied!", status=status.HTTP_403_FORBIDDEN, content_type="text/plain")
                    else:
                        return HttpResponse(f"User '{username}' does not exist!", status=status.HTTP_400_BAD_REQUEST, content_type="text/plain")
                else:
                    # Request is not authenticated
                    # Create new profile
                    serializer = self.serializer_class(data={"following": [],"user": data})
                    # Check if data is valid
                    if not serializer.is_valid():
                        return HttpResponse("Error creating user profile!", status=status.HTTP_400_BAD_REQUEST, content_type="text/plain")
                    # Create user
                    serializer.save()
                    # Return HTTP 201 CREATED signal
                    return HttpResponse(f"User {username} created!", status=status.HTTP_201_CREATED, content_type="text/plain")
            except:
                return HttpResponse("Error creating account!", status=status.HTTP_400_BAD_REQUEST, content_type="text/plain")

        def delete(self, request, username):
            """
            Check if user exists
            If authenticated:
                If superuser or user.username == username
                    Delete user
            """
            try:
                # Username can only be lowercase
                username = username.lower()
                if request.user.is_authenticated:
                    if request.user.username.lower() == username.lower() or request.user.is_superuser:
                        # Check if user exists
                        user_filter = User.objects.filter(username=username)
                        if user_filter.exists():
                            # Fetch user
                            user = User.objects.get(username=username)

                            # Admin cannot be deleted
                            if username.lower() == "admin":
                                return HttpResponse("Admin user cannot be deleted!", status=status.HTTP_403_FORBIDDEN, content_type="text/plain")

                            # Superuser cannot be deleted by anyone but by admin
                            if user.is_superuser and request.user.username != "admin":
                                return HttpResponse("Superusers can only be deleted by the admin!", status=status.HTTP_403_FORBIDDEN, content_type="text/plain")

                            # Delete user
                            user.delete()
                            return HttpResponse(f"User {username} deleted!", status=status.HTTP_200_OK, content_type="text/plain")
                        else:
                            return HttpResponse("Account with given username doesn't exist!", status=status.HTTP_400_BAD_REQUEST, content_type="text/plain")
                    else:
                        return HttpResponse("Error deleting account, access denied!", status=status.HTTP_403_FORBIDDEN, content_type="text/plain")
                else:
                    return HttpResponse("Error deleting account, not authenticated!", status=status.HTTP_401_UNAUTHORIZED, content_type="text/plain")
            except:
                return HttpResponse("Error deleting account!", status=status.HTTP_400_BAD_REQUEST, content_type="text/plain")
