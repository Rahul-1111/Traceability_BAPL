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
OUTPUT_DIR = os.path.join(BASE_DIR, "Qr")
SERIAL_FILE = os.path.join(BASE_DIR, "serial_number.txt")

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
    """Serial starts at 00001, increments each call, resets to 00001 after 99999. No month reset."""
    last_serial = 0  # ✅ Default

    if os.path.exists(SERIAL_FILE):
        with open(SERIAL_FILE, "r") as file:
            content = file.read().strip()
            try:
                last_serial = int(content)  # ✅ Just read the number, no month
            except ValueError:
                last_serial = 0  # ✅ Reset if file corrupted

    if last_serial >= 99999:
        new_serial = 1            # ✅ Rollover 99999 → 00001
    else:
        new_serial = last_serial + 1  # ✅ Increment

    with open(SERIAL_FILE, "w") as file:
        file.write(str(new_serial))  # ✅ Save number only, no month

    return str(new_serial).zfill(5)  # ✅ Always 5 digits: 00001

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

def generate_qr_code(prefix, _serial_number=None):
    """Generates QR Code with format: [PREFIX]-DDMMYY[SERIAL]"""

    clear_old_qr_codes()

    now = datetime.datetime.now()
    date_part = now.strftime("%d%m%y")
    unique_serial = get_next_serial_number()  # ✅ 5-digit serial no month reset

    qr_data = f"{prefix}-{date_part}{unique_serial}"  # ✅ Format: PREFIX-DDMMYY00001

    zpl_qrcode = generate_zpl_qrcode(qr_data)
    print_zpl(zpl_qrcode)

    generate_qrcode_image(qr_data)

    logger.info(f"🖨️ Printed QR: {qr_data}")

    return f"✅ QR Code Generated: {qr_data}"

# Example usage:
if __name__ == "__main__":
    sample_prefix = "556043200181"
    sample_serial = 12345  # ✅ Ignored, sequential numbers are used
    print(generate_qr_code(sample_prefix, sample_serial))