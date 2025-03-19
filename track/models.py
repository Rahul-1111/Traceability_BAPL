from django.db import models

class TraceabilityData(models.Model):
    sr_no = models.AutoField(primary_key=True)  # Serial Number (Primary Key)
    part_number = models.CharField(max_length=100, unique=True)  # QR Code
    date = models.DateField()  # Date of entry
    time = models.TimeField()  # Time of entry
    shift = models.CharField(max_length=10, null=True, blank=True)  # Shift (e.g., A, B, C)
    st1_result = models.CharField(max_length=10, null=True, blank=True)  # Station 1 Result
    st2_result = models.CharField(max_length=10, null=True, blank=True)  # Station 2 Result
    st3_result = models.CharField(max_length=10, null=True, blank=True)  # Station 3 Result
    st4_result = models.CharField(max_length=10, null=True, blank=True)  # Station 4 Result
    st5_result = models.CharField(max_length=10, null=True, blank=True)  # Station 5 Result

    def __str__(self):
        return f"{self.sr_no} - {self.part_number}"
