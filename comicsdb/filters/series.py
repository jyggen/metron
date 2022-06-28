import operator
from functools import reduce

from django.db.models import Q
from django_filters import rest_framework as filters

from comicsdb.models import Series


class SeriesNameFilter(filters.CharFilter):
    def filter(self, qs, value):
        if value:
            query_list = value.split()
            qs = qs.filter(reduce(operator.and_, (Q(name__icontains=q) for q in query_list)))
        return qs


class SeriesFilter(filters.FilterSet):
    name = SeriesNameFilter(lookup_expr="icontains")
    publisher_id = filters.filters.NumberFilter(
        field_name="publisher__id", lookup_expr="exact"
    )
    publisher_name = filters.CharFilter(field_name="publisher__name", lookup_expr="icontains")
    series_type_id = filters.filters.NumberFilter(
        field_name="series_type__id", lookup_expr="exact"
    )
    series_type = filters.CharFilter(field_name="series_type__name", lookup_expr="icontains")

    class Meta:
        model = Series
        fields = ["volume", "year_began", "year_end"]
