from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    model = get_user_model()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]