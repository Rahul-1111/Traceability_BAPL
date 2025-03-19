from django.contrib import admin
from .models import TraceabilityData

class TraceabilityDataAdmin(admin.ModelAdmin):
    list_display = (
        'sr_no', 'part_number', 'date', 'formatted_time', 'shift',
        'st1_result', 'st2_result', 'st3_result', 'st4_result', 'st5_result',
    )
    list_filter = ('date', 'shift', 'st1_result', 'st2_result', 'st3_result', 'st4_result', 
                   'st5_result')
    search_fields = ('part_number', 'date')
    ordering = ('date',)
    list_per_page = 25

    # ✅ Custom method to format time in HHMMSS
    def formatted_time(self, obj):
        return obj.time.strftime("%H:%M:%S") if obj.time else ""
    
    formatted_time.short_description = "Time (HHMMSS)"  # ✅ Change column name

admin.site.site_header = "Traceability Management System"
admin.site.site_title = "Traceability Admin Panel"
admin.site.index_title = "Welcome to the Traceability Dashboard"

admin.site.register(TraceabilityData, TraceabilityDataAdmin)
