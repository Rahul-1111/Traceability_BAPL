from django.db import models

class TraceabilityData(models.Model):
    sr_no = models.AutoField(primary_key=True)  # Serial Number (Primary Key)
    part_number = models.CharField(max_length=100, unique=True)  # QR Code
    date = models.DateField()  # Date of entry
    time = models.TimeField()  # Time of entry
    shift = models.CharField(max_length=10, null=True, blank=True)  # Shift (e.g., A, B, C)
    # ✅ Station 1
    st1_result = models.CharField(max_length=10, null=True, blank=True)
    st1_datetime = models.DateTimeField(null=True, blank=True)  # ✅ Combined

    # ✅ Station 2
    st2_result = models.CharField(max_length=10, null=True, blank=True)
    st2_datetime = models.DateTimeField(null=True, blank=True)  # ✅ Combined

    # ✅ Station 3
    st3_result = models.CharField(max_length=10, null=True, blank=True)
    st3_datetime = models.DateTimeField(null=True, blank=True)  # ✅ Combined

    # ✅ Station 4
    st4_result = models.CharField(max_length=10, null=True, blank=True)
    st4_datetime = models.DateTimeField(null=True, blank=True)  # ✅ Combined

    # ✅ Station 5
    st5_result = models.CharField(max_length=10, null=True, blank=True)
    st5_datetime = models.DateTimeField(null=True, blank=True)  # ✅ Combined

    # ✅ Station 6
    st6_result = models.CharField(max_length=10, null=True, blank=True)
    st6_datetime = models.DateTimeField(null=True, blank=True)  # ✅ Combined

    def __str__(self):
        return f"{self.sr_no} - {self.part_number}"
