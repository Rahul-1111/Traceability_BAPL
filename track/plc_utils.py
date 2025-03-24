import pymcprotocol
import time
import logging
from track.models import TraceabilityData
from datetime import datetime
import struct
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define PLCs for each station
PLC_MAPPING = {
    "st1": {"ip": "192.168.1.110"},
    "st2": {"ip": "192.168.1.120"},
    "st3": {"ip": "192.168.1.130"},
    "st4": {"ip": "192.168.1.140"},
    "st5": {"ip": "192.168.1.130"},
}

# Define Registers for each station
REGISTERS = {
    "st1": {"qr": 2700, "result": 2723, "scan_trigger": 2721, "write_signal": 2725},
    "st2": {"qr": 2700, "result": 2723, "scan_trigger": 2721, "write_signal": 2725},
    "st3": {"qr": 2700, "result": 2723, "scan_trigger": 2721, "write_signal": 2725},
    "st4": {"qr": 2700, "result": 2723, "scan_trigger": 2721, "write_signal": 2725},
    "st5": {"qr": 3700, "result": 3723, "scan_trigger": 3721, "write_signal": 3725},
}

# QR Code validation pattern
QR_PATTERN = re.compile(r"^\d{12}-\d{11}$")

def connect_to_plc(plc_ip):
    mc = pymcprotocol.Type3E()
    try:
        mc.connect(plc_ip, 5007)
        logger.info(f"✅ Connected to PLC {plc_ip}")
        return mc
    except Exception as e:
        logger.error(f"❌ Failed to connect to PLC {plc_ip}: {e}")
        return None

def read_register(mc, address, num_registers=1):
    try:
        response = mc.batchread_wordunits(headdevice=f"D{address}", readsize=num_registers)
        return response if response else None
    except Exception as e:
        logger.error(f"❌ Error reading register {address}: {e}")
        return None

def write_register(mc, address, value):
    try:
        mc.batchwrite_wordunits(headdevice=f"D{address}", values=[value])
        logger.info(f"✅ Wrote {value} to register {address}")
    except Exception as e:
        logger.error(f"❌ Error writing to register {address}: {e}")

def fetch_station_data():
    station_data = {}
    for station, plc in PLC_MAPPING.items():
        mc = connect_to_plc(plc["ip"])
        if not mc:
            continue

        reg = REGISTERS[station]
        scan_trigger = read_register(mc, reg["scan_trigger"], 1)
        if not scan_trigger or scan_trigger[0] != 1:
            logger.info(f"🚫 {station}: No scan trigger")
            mc.close()
            continue

        qr_registers = read_register(mc, reg["qr"], 21)
        result = read_register(mc, reg["result"], 1)
        mc.close()

        if qr_registers and result:
            qr_string = convert_registers_to_string(qr_registers)
            result_value = "OK" if result[0] == 1 else "NOT OK"
            station_data[station] = {"qr": qr_string, "result": result_value}

    return station_data

def convert_registers_to_string(registers):
    try:
        byte_array = b"".join(struct.pack("<H", reg) for reg in registers)
        return byte_array.decode("ascii", errors="ignore").replace("\x00", "").strip()
    except Exception as e:
        logger.error(f"❌ Error converting register data: {e}")
        return ""

def update_traceability_data():
    while True:
        station_data = fetch_station_data()

        for station, data in station_data.items():
            part_number = data["qr"].strip()
            plc = PLC_MAPPING[station]
            reg = REGISTERS[station]

            mc = connect_to_plc(plc["ip"])
            if not mc:
                continue

            if not QR_PATTERN.match(part_number):
                logger.warning(f"🚫 {station}: Invalid QR format - '{part_number}'. Writing 4 to write_signal.")
                write_register(mc, reg["write_signal"], 4)
                mc.close()
                continue

            obj = TraceabilityData.objects.filter(part_number=part_number).first()

            if obj:
                logger.info(f"🟡 Updating existing record for part: {part_number}")
            else:
                obj = TraceabilityData.objects.create(
                    part_number=part_number,
                    date=datetime.today().date(),
                    time=datetime.now().time(),
                    shift=get_current_shift()
                )
                logger.info(f"🟢 Created new record for part: {part_number}")

            station_num = int(station[2])
            previous_station = f"st{station_num - 1}" if station_num > 1 else None
            previous_status = getattr(obj, f"{previous_station}_result", None) if previous_station else None

            if previous_station and previous_status in [None, "NOT OK"]:
                logger.warning(f"🚨 {station}: Previous station '{previous_station}' result is '{previous_status}'. Blocking operation.")
                write_register(mc, reg["write_signal"], 8)
                mc.close()
                continue

            existing_ok = getattr(obj, f"{station}_result", None) == "OK"

            if existing_ok:
                write_register(mc, reg["write_signal"], 2)
                write_register(mc, reg["scan_trigger"], 0)
                logger.info(f"🟢 {station}: Part '{part_number}' is already OK. Sending 2.")
                mc.close()
                continue

            result = read_register(mc, reg["result"], 1)
            result_value = "OK" if result and result[0] == 1 else "NOT OK"

            setattr(obj, f"{station}_result", result_value)
            obj.save()

            write_signal = 2 if result_value == "OK" else 1
            write_register(mc, reg["write_signal"], write_signal)

            if write_signal in [1, 2]:
                time.sleep(1)
                write_register(mc, reg["scan_trigger"], 0)

            mc.close()
        time.sleep(1)

def get_current_shift():
    now = datetime.now().time()
    if datetime.strptime("07:00", "%H:%M").time() <= now < datetime.strptime("15:30", "%H:%M").time():
        return 'Shift 1'
    elif datetime.strptime("15:30", "%H:%M").time() <= now < datetime.strptime("23:59", "%H:%M").time():
        return 'Shift 2'
    else:
        return 'Shift 3'