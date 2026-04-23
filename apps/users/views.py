from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])  # важно — иначе не зарегистрируешься
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")
    role = request.data.get("role", "student")

    if not username or not password:
        return Response({"error": "username and password required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "user already exists"}, status=400)

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        role=role
    )

    return Response({
        "message": "user created",
        "username": user.username,
        "role": user.role
    }, status=201)
