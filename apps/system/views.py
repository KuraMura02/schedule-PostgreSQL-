from rest_framework import viewsets
from rest_framework.response import Response

from core.permissions import SystemSettingsPermission

from .models import SystemSettings
from .serializers import SystemSettingsSerializer


class SystemSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = SystemSettingsSerializer
    permission_classes = [SystemSettingsPermission]

    def get_queryset(self):
        return SystemSettings.objects.all()

    def create(self, request, *args, **kwargs):
        instance = SystemSettings.get_solo()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(singleton_enforcer=1)
        return Response(serializer.data, status=200)
