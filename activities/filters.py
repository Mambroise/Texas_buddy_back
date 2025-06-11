import django_filters
from .models.activity import Activity

class ActivityFilter(django_filters.FilterSet):
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')
    category = django_filters.UUIDFilter(field_name='category__id')

    class Meta:
        model = Activity
        fields = ['category', 'has_discount']

    def filter_has_discount(self, queryset, name, value):
        if value:
            return queryset.exclude(discount__isnull=True)
        return queryset
