import django_filters
from django import forms
from .models import TraceabilityData

class TraceabilityDataFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name="date", lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "date", "class": "custom-input"})
    )
    end_date = django_filters.DateFilter(
        field_name="date", lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "date", "class": "custom-input"})
    )

    class Meta:
        model = TraceabilityData
        fields = ['part_number', 'start_date', 'end_date', 'shift']
