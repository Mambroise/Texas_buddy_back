# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/mixin.py
# Author : Morice
# ---------------------------------------------------------------------------


import logging
logger = logging.getLogger("texasbuddy")


class RetrieveLogMixin:
    """
    Generic mixin to log retrieve operations.
    Use it with RetrieveAPIView or any view with .retrieve() method.
    """

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        instance = self.get_object()
        logger.info(
            "[%s_RETRIEVE] %s retrieved by user %s",
            instance.__class__.__name__.upper(),
            getattr(instance, "id", "N/A"),
            request.user.email
        )
        return response
    
    
class ListLogMixin:
    """
    Generic mixin to log list operations.
    Use with ListAPIView.
    """
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        logger.info(
            "[%s_LIST] %d items retrieved by user %s",
            self.serializer_class.Meta.model.__name__.upper(),
            len(response.data),
            request.user.email if request.user.is_authenticated else "Anonymous"
        )
        return response



class CRUDLogMixin:
    """
    Generic mixin to log create, update, delete operations.
    Use with CreateAPIView, UpdateAPIView, DestroyAPIView or ModelViewSet.
    """

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            "[%s_CREATE] %s created by user %s",
            instance.__class__.__name__.upper(),
            getattr(instance, "id", "N/A"),
            self.request.user.email
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(
            "[%s_UPDATE] %s updated by user %s",
            instance.__class__.__name__.upper(),
            getattr(instance, "id", "N/A"),
            self.request.user.email
        )

    def perform_destroy(self, instance):
        logger.info(
            "[%s_DELETE] %s deleted by user %s",
            instance.__class__.__name__.upper(),
            getattr(instance, "id", "N/A"),
            self.request.user.email
        )
        instance.delete()
