from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts import serializers

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):

    """create: Login in with email and password."""
    serializer_class = serializers.CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):

    """Sign up as a new user"""
    serializer_class = serializers.CreateUserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]


class DashboardViewset(viewsets.ModelViewSet):

    """
    list: Returns current user's dashboard (Profile info).
    partial_update: Update user data.
    destroy: Delete user account by ID.
    """
    serializer_class = serializers.RetrieveUserSerializer
    queryset = User.objects.all()
    http_method_names = ["get", "patch", "delete"]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == "partial_update":
            return serializers.UpdateUserSerializer
        return super().get_serializer_class()

    def list(self, request):
        if not request.user.is_superuser:
            queryset = User.objects.get(id=request.user.id)
            serializer = serializers.RetrieveUserSerializer(queryset, many=False)
            return Response({
                "discussion_count": request.user.discussions.all().count(),
                **serializer.data
            }, status=status.HTTP_200_OK)

        queryset = User.objects.all()
        query = self.paginate_queryset(queryset)

        serializer = serializers.RetrieveUserSerializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)
