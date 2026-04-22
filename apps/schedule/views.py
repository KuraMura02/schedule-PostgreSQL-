import logging

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.services import notify_schedule_change, notify_schedule_import
from core.permissions import SchedulePermission

from .models import Schedule
from .serializers import ExportQuerySerializer, ScheduleImportSerializer, ScheduleSerializer
from .services.export_service import ScheduleExportService
from .services.import_service import ScheduleImportService


logger = logging.getLogger(__name__)


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.select_related("teacher", "course")
    serializer_class = ScheduleSerializer
    permission_classes = [SchedulePermission]
    filterset_fields = ["day", "course", "teacher", "student_group"]
    search_fields = ["room", "student_group", "course__name", "course__code", "teacher__username"]
    ordering_fields = ["day", "start_time", "end_time", "room", "created_at"]
    ordering = ["day", "start_time"]

    def perform_create(self, serializer):
        schedule = serializer.save()
        notify_schedule_change(schedule=schedule, actor=self.request.user, action="created")

    def perform_update(self, serializer):
        schedule = serializer.save()
        notify_schedule_change(schedule=schedule, actor=self.request.user, action="updated")

    def perform_destroy(self, instance):
        notify_schedule_change(schedule=instance, actor=self.request.user, action="deleted")
        instance.delete()

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        serializer = ExportQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        export_format = serializer.validated_data["format"]

        service = ScheduleExportService(queryset=self.filter_queryset(self.get_queryset()))
        try:
            content, content_type, filename = service.export(export_format=export_format)
        except NotImplementedError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_501_NOT_IMPLEMENTED)

        response = HttpResponse(content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class ScheduleImportView(APIView):
    permission_classes = [SchedulePermission]

    def post(self, request, *args, **kwargs):
        serializer = ScheduleImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ScheduleImportService(uploaded_file=serializer.validated_data["file"], actor=request.user)
        result = service.process()
        logger.info("Schedule import finished: %s", result["summary"])
        notify_schedule_import(result=result, actor=request.user)
        return Response(result, status=status.HTTP_201_CREATED if result["summary"]["imported_rows"] else status.HTTP_200_OK)
