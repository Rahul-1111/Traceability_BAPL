from django.shortcuts import render
from django.http import JsonResponse
from .models import TraceabilityData
import logging
from .qr_utils import generate_qr_code  # ✅ Using latest QR code function
import random
import datetime
from pymodbus.client import ModbusTcpClient
import time
import threading
from .plc_utils import PLC_MAPPING 

logger = logging.getLogger(__name__)
# Shared dictionary for storing PLC statuses
plc_statuses = {}

def monitor_plcs():
    """Continuously monitor PLC connections in a background thread."""
    global plc_statuses
    while True:
        temp_statuses = {}
        for station, plc in PLC_MAPPING.items():
            plc_ip = plc.get("ip")
            if not plc_ip:
                continue  # Skip if no IP

            client = ModbusTcpClient(plc_ip, port=5007, timeout=1)
            is_connected = client.connect()
            client.close()

            temp_statuses[station] = "connected" if is_connected else "disconnected"

        plc_statuses = temp_statuses  # Update shared status dictionary
        time.sleep(1)  # Retry every 2 seconds

# Start the monitoring thread once
plc_monitor_thread = threading.Thread(target=monitor_plcs, daemon=True)
plc_monitor_thread.start()

def plc_status(request):
    """Return PLC statuses with combined stations for shared PLCs."""
    plc_statuses = {}

    for station, plc in PLC_MAPPING.items():
        plc_ip = plc.get("ip")  
        if not plc_ip:
            continue  # Skip stations with missing IPs

        client = ModbusTcpClient(plc_ip, port=5007, timeout=1)
        is_connected = client.connect()
        client.close()

        plc_statuses[station] = "connected" if is_connected else "disconnected"

    # Combine shared PLCs
    combined_statuses = {
        "St 1": plc_statuses.get("st1", "disconnected"),
        "St 2": plc_statuses.get("st2", "disconnected"),
        "St 3 & 5": plc_statuses.get("st3", "disconnected"),  # Shared PLC for St3 & St4
        "St 4": plc_statuses.get("st5", "disconnected"),  # Shared PLC for St5 & St6
    }

    # Count connected and disconnected PLCs
    connected_count = sum(1 for status in combined_statuses.values() if status == "connected")
    disconnected_count = sum(1 for status in combined_statuses.values() if status == "disconnected")

    return JsonResponse({
        "plc_statuses": combined_statuses,
        "connected_count": connected_count,
        "disconnected_count": disconnected_count
    })

# ✅ Render the main page
def combined_page(request):
    return render(request, 'track/combined_page.html')

# View to handle QR code generation# View to handle QR code generation
def generate_qr_code_view(request):
    if request.method == "POST":
        prefix = request.POST.get("prefix")  # ✅ Get selected prefix
        serial_number = random.randint(10000, 99999)  # ✅ Generate unique 5-digit serial

        if not prefix:
            return JsonResponse({"error": "Prefix is required"}, status=400)

        try:
            response_message = generate_qr_code(prefix, serial_number)
            return JsonResponse({"message": response_message, "generated_code": f"{prefix}-{datetime.datetime.now().strftime('%d%m%y')}-{serial_number}"})

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=500)

from datetime import date
from django.db.models import Q

def fetch_torque_data(request):
    if request.method == "GET":
        today = date.today()  # Get today's date
        
        # Filter for today's records
        today_records = TraceabilityData.objects.filter(date=today)

        # Filter for "NOT OK" or NULL/blank records (without date restriction)
        not_ok_or_null_records = TraceabilityData.objects.filter(
            Q(st1_result="NOT OK") | Q(st2_result="NOT OK") |
            Q(st3_result="NOT OK") | Q(st4_result="NOT OK") |
            Q(st5_result="NOT OK") | Q(st6_result="NOT OK") |
            Q(st1_result__isnull=True) | Q(st2_result__isnull=True) |
            Q(st3_result__isnull=True) | Q(st4_result__isnull=True) |
            Q(st5_result__isnull=True) | Q(st6_result__isnull=True) |
            Q(st1_result="") | Q(st2_result="") | Q(st3_result="") |
            Q(st4_result="") | Q(st5_result="") | Q(st6_result="")
        )

        # Combine both querysets and order by date & time (newest first)
        combined_data = (today_records | not_ok_or_null_records).distinct().order_by('-date', '-time')

        formatted_data = [
            {
                "part_number": item.part_number,
                "date": item.date.strftime("%Y-%m-%d") if item.date else "",
                "time": item.time.strftime("%H:%M:%S") if item.time else "",
                "shift": item.shift,
                "st1_result": item.st1_result,
                "st2_result": item.st2_result,
                "st3_result": item.st3_result,
                "st4_result": item.st4_result,
                "st5_result": item.st5_result,
                "st6_result": item.st6_result,
            }
            for item in combined_data
        ]
        
        return JsonResponse({"data": formatted_data})

from .filters import TraceabilityDataFilter

def search_parts(request):
    queryset = TraceabilityData.objects.all()
    filter = TraceabilityDataFilter(request.GET, queryset=queryset)
    return render(request, 'track/search_parts.html', {'filter': filter})
