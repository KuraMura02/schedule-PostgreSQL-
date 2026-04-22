from django.utils import timezone
from rest_framework import filters, viewsets

from core.permissions import NotificationPermission

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [NotificationPermission]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Notification.objects.select_related("user")
        user = self.request.user
        if user.is_authenticated and user.role != "admin":
            queryset = queryset.filter(user=user)
        return queryset

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.is_read and instance.read_at is None:
            instance.read_at = timezone.now()
            instance.save(update_fields=["read_at", "updated_at"])
