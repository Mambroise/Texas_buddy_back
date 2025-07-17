# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :community/views/review_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.generics import get_object_or_404

from community.models import Review
from community.serializers import ReviewSerializer
from community.services.review_service import ReviewService
from core.throttles import PostRateLimitedAPIView, GetRateLimitedAPIView

import logging
logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReviewListCreateView(PostRateLimitedAPIView, GetRateLimitedAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request, *args, **kwargs):
        # Vérification des cibles
        activity_id = request.query_params.get('activity_id')
        event_id = request.query_params.get('event_id')

        if not activity_id and not event_id:
            return Response({'error': 'one activity or event is required.'}, status=400)

        if activity_id and event_id:
            return Response({'error': 'Only one activity OR event is required.'}, status=400)

        # Construction du queryset
        if activity_id:
            queryset = Review.objects.filter(activity_id=activity_id).select_related('user')
        else:
            queryset = Review.objects.filter(event_id=event_id).select_related('user')

        # Filtrage par note minimale / maximale
        min_rating = request.query_params.get('min_rating')
        max_rating = request.query_params.get('max_rating')

        if min_rating:
            try:
                queryset = queryset.filter(rating__gte=float(min_rating))
            except ValueError:
                pass

        if max_rating:
            try:
                queryset = queryset.filter(rating__lte=float(max_rating))
            except ValueError:
                pass

        queryset = queryset.order_by('-created_at')

        # Pagination
        paginator = self.pagination_class()
        paginated_qs = paginator.paginate_queryset(queryset, request)
        serializer = ReviewSerializer(paginated_qs, many=True, context={'request': request})

        # Log
        logger.info(
            "[REVIEW_LIST] %d items retrieved by user %s",
            len(serializer.data),
            request.user.email if request.user.is_authenticated else "Anonymous"
        )

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Création d'une review
        target_type = request.data.get('target_type')  # 'activity' ou 'event'
        target_id = request.data.get('target_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')

        if not target_type or not target_id or rating is None:
            return Response({'error': 'target_type, target_id, rating are required.'}, status=400)

        try:
            review = ReviewService.create_review(request.user, target_type, target_id, rating, comment)

            # Log
            logger.info(
                "[REVIEW_CREATE] %s review created by user %s",
                target_type.upper(),
                request.user.email
            )

            return Response(ReviewSerializer(review).data, status=201)

        except Exception as e:
            logger.exception(f"Failed to create review: {e}")
            return Response({'error': str(e)}, status=400)



class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        """
        Mise à jour d'une review existante (seulement par son auteur).
        """
        review = get_object_or_404(Review, pk=pk)

        # Vérifie que l'utilisateur est bien l'auteur
        if review.user != request.user:
            return Response({'error': 'You cannot edit someone else review.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ReviewSerializer(review, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info("[REVIEW_UPDATE] Review %s updated by user %s",
                        review.id, request.user.email)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """
        Suppression d'une review existante (seulement par son auteur).
        """
        review = get_object_or_404(Review, pk=pk)

        if review.user != request.user:
            return Response({'error': 'You cannot delete someone else review.'},
                            status=status.HTTP_403_FORBIDDEN)

        review.delete()
        logger.info("[REVIEW_DELETE] Review %s deleted by user %s",
                    pk, request.user.email)
        return Response(status=status.HTTP_204_NO_CONTENT)
