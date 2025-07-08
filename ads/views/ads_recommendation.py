# # ads/views/ads_recommendation.py

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.utils.timezone import now
# from django.contrib.gis.geos import Point
# from django.contrib.gis.db.models.functions import Distance
# from ..models import Advertisement
# from ..serializers import AdvertisementSerializer
# from core.throttles import GetRateLimitedAPIView


# class GetRecommendedAdView(GetRateLimitedAPIView):
#     """
#     Recommande une pub adaptée selon le contexte (type, position, interet user, validité…)
#     """
#     permission_classes = []  # Public
#     throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

#     def get(self, request):
#         ad_type = request.query_params.get("ad_type")  # e.g., "NATIVE"
#         lat = request.query_params.get("lat")
#         lng = request.query_params.get("lng")

#         queryset = Advertisement.objects.filter(
#             start_date__lte=now().date(),
#             end_date__gte=now().date(),
#             ad_type=ad_type,
#             partner__is_active=True
#         )

#         if lat and lng:
#             user_point = Point(float(lng), float(lat))
#             queryset = queryset.filter(location__distance_lte=(user_point, 100000))  # 100km max
#             queryset = queryset.annotate(distance=Distance("location", user_point)).order_by("distance")

#         ad = queryset.first()
#         if not ad:
#             return Response({"detail": "No ad available"}, status=204)

#         serializer = AdvertisementSerializer(ad)
#         return Response(serializer.data)
