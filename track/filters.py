import django_filters
from .models import TraceabilityData

SHIFT_CHOICES = [
    ("Shift 1", "Shift 1"),
    ("Shift 2", "Shift 2"),
    ("Shift 3", "Shift 3"),
]

class TraceabilityDataFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='date', lookup_expr='gte', label='Start Date')
    end_date = django_filters.DateFilter(field_name='date', lookup_expr='lte', label='End Date')
    shift = django_filters.ChoiceFilter(choices=SHIFT_CHOICES, label="Shift")

    class Meta:
        model = TraceabilityData
        fields = ['part_number', 'shift', 'start_date', 'end_date']
