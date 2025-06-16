# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/filters.py
# Author : Morice
# ---------------------------------------------------------------------------

import django_filters
from django.utils import timezone
from datetime import datetime
from .models import Activity, Event


class ActivityFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method='filter_by_categories')
    has_promotion = django_filters.BooleanFilter(method='filter_has_promotion')
    date = django_filters.DateFilter(method='filter_has_promotion')

    class Meta:
        model = Activity
        fields = ['category', 'has_promotion', 'date']

    def filter_by_categories(self, queryset, name, value):
        categories = [cat.strip() for cat in value.split(',')]
        return queryset.filter(category__name__in=categories).distinct()

    def filter_has_promotion(self, queryset, name, value):
        request = self.request
        target_date_str = request.GET.get("date")
        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date() if target_date_str else timezone.now().date()
        except ValueError:
            target_date = timezone.now().date()

        if str(value).lower() in ['true', '1']:
            return queryset.filter(
                promotions__is_active=True,
                promotions__start_date__lte=target_date,
                promotions__end_date__gte=target_date
            ).distinct()
        return queryset


class EventFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method='filter_by_categories')
    has_promotion = django_filters.BooleanFilter(method='filter_has_promotion')
    date = django_filters.DateFilter(method='filter_has_promotion')

    class Meta:
        model = Event
        fields = ['category', 'has_promotion', 'date']

    def filter_by_categories(self, queryset, name, value):
        categories = [cat.strip() for cat in value.split(',')]
        return queryset.filter(category__name__in=categories).distinct()

    def filter_has_promotion(self, queryset, name, value):
        request = self.request
        target_date_str = request.GET.get("date")
        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date() if target_date_str else timezone.now().date()
        except ValueError:
            target_date = timezone.now().date()

        if str(value).lower() in ['true', '1']:
            return queryset.filter(
                promotions__is_active=True,
                promotions__start_date__lte=target_date,
                promotions__end_date__gte=target_date
            ).distinct()
        return queryset
