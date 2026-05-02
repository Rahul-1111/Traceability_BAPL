from django.contrib import admin
from .models import TraceabilityData

class TraceabilityDataAdmin(admin.ModelAdmin):
    list_display = (
        'sr_no', 'part_number', 'date', 'formatted_time', 'shift',
        'st1_result', 'st1_datetime',
        'st2_result', 'st2_datetime',
        'st3_result', 'st3_datetime',
        'st4_result', 'st4_datetime',
        'st5_result', 'st5_datetime',
        'st6_result', 'st6_datetime',
    )
    list_filter = (
        'date', 'shift',
        'st1_result', 'st2_result', 'st3_result',
        'st4_result', 'st5_result', 'st6_result',
    )
    search_fields = ('part_number', 'date')
    ordering = ('date',)
    list_per_page = 25

    # ✅ Format entry time in HH:MM:SS
    def formatted_time(self, obj):
        return obj.time.strftime("%H:%M:%S") if obj.time else ""
    formatted_time.short_description = "Time (HH:MM:SS)"

admin.site.site_header = "Traceability Management System"
admin.site.site_title = "Traceability Admin Panel"
admin.site.index_title = "Welcome to the Traceability Dashboard"
admin.site.register(TraceabilityData, TraceabilityDataAdmin)