from zebra import Zebra
import qrcode
import datetime
import logging
import os

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Get Current Project Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
OUTPUT_DIR = os.path.join(BASE_DIR, "Qr")  # ✅ Save in "Qr" folder
SERIAL_FILE = os.path.join(BASE_DIR, "serial_number.txt")  # ✅ Store last used serial & date

# ✅ Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clear_old_qr_codes():
    """Deletes QR codes older than 2 days."""
    today_str = datetime.datetime.now().strftime("%d%m%y")
    yesterday_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%d%m%y")

    for filename in os.listdir(OUTPUT_DIR):
        if today_str not in filename and yesterday_str not in filename:
            file_path = os.path.join(OUTPUT_DIR, filename)
            try:
                os.remove(file_path)
                logger.info(f"🗑️ Deleted old QR: {filename}")
            except Exception as e:
                logger.error(f"❌ Error deleting file {filename}: {e}")

def get_next_serial_number():
    """Reads the last serial number from a file, resets if a new month, and updates the file."""
    current_month = datetime.datetime.now().strftime("%m%y")  # Format: MMYY

    if os.path.exists(SERIAL_FILE):
        with open(SERIAL_FILE, "r") as file:
            try:
                last_month, last_serial = file.read().strip().split(",")  # Read last month & serial
                last_serial = int(last_serial)
            except ValueError:
                last_month, last_serial = current_month, 0  # Reset if file is corrupted
    else:
        last_month, last_serial = current_month, 0  # Start from 0 if file doesn't exist

    # ✅ Reset if a new month has started
    if last_month != current_month:
        new_serial = 1
    else:
        new_serial = last_serial + 1

    # ✅ Save the updated month and serial number
    with open(SERIAL_FILE, "w") as file:
        file.write(f"{current_month},{new_serial}")

    return str(new_serial).zfill(5)  # Ensure 5-digit serial number (e.g., 00001)

def generate_zpl_qrcode(qr_data):
    """Generates ZPL code for printing a QR code on a Zebra printer."""
    zpl = f"""
    ^XA
    ^PW160
    ^LL100
    ^FT35,120^BQN,2,4
    ^FH\\^FDLA,{qr_data}^FS
    ^PQ1,0,1,Y
    ^XZ
    """
    return zpl

def print_zpl(zpl_command):
    """Sends ZPL command to the Zebra printer."""
    try:
        z = Zebra()
        z.setqueue("TSC TE210")  
        z.output(zpl_command)
        logger.info("✅ ZPL command sent successfully.")
    except Exception as e:
        logger.error(f"❌ Error sending ZPL to printer: {e}")

def generate_qrcode_image(qr_data):
    """Generates and saves a QR code image."""
    filename = f"qrcode_{qr_data}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(filepath)
    
    logger.info(f"🖼️ QR saved: {filepath}")

def generate_qr_code(prefix, _serial_number=None):  # ✅ `_serial_number` is ignored
    """Generates QR Code with format: [PREFIX]-DDMMYY[SERIAL]"""

    clear_old_qr_codes()  # ✅ Delete old QR codes before generating a new one

    now = datetime.datetime.now()
    date_part = now.strftime("%d%m%y")  # ddmmyy (last two digits of year)
    unique_serial = get_next_serial_number()  # ✅ Automatically get next serial

    qr_data = f"{prefix}-{date_part}{unique_serial}"  # ✅ Format: PREFIX-DDMMYY00001

    zpl_qrcode = generate_zpl_qrcode(qr_data)
    print_zpl(zpl_qrcode)

    generate_qrcode_image(qr_data)

    logger.info(f"🖨️ Printed QR: {qr_data}")

    return f"✅ QR Code Generated: {qr_data}"

# Example usage:
if __name__ == "__main__":
    sample_prefix = "PDU-S-10594-1"
    sample_serial = 12345  # ✅ This is ignored, sequential numbers are used
    print(generate_qr_code(sample_prefix, sample_serial))
