#!/usr/bin/env python3
import subprocess
import random
import re
import logging
import time
from MakeOp import create_directory
import shutil
import sys

# Logging Setup
def setup_logging():
    logging.basicConfig(
        filename='pregame.log',
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(message)s',
        filemode='a'
    )

# Constants
GOOD_OUIS = ['64:1b:2f', '9c:73:b1', '38:8a:06']
BAD_OUIS = ['9c:ef:d5', '00:c0:ca']
RETRY_LIMIT = 3
MAC_PATTERN = re.compile(r'^([0-9a-f]{2}[:-]){5}([0-9a-f]{2})$')
REQUIRED_TOOLS = ['macchanger', 'iw', 'ip']

# Utility Functions
def check_mac_address(mac):
    """Checks if MAC prefix is in GOOD_OUIS."""
    mac_prefix = mac[:8].lower()
    return 'GOOD' if mac_prefix in GOOD_OUIS else 'BAD'

def validate_mac_address(mac):
    """Validates MAC address format."""
    return bool(MAC_PATTERN.match(mac.lower()))

def check_prerequisites():
    """Ensure all required system tools are installed."""
    missing = [tool for tool in REQUIRED_TOOLS if not shutil.which(tool)]
    if missing:
        logging.critical(f"Missing prerequisites: {', '.join(missing)}")
        print(f"[ERROR] Missing required tools: {', '.join(missing)}. Please install them.")
        sys.exit(1)
    logging.info("All prerequisites installed.")

def get_available_interfaces():
    """List available wireless interfaces using iw dev."""
    try:
        output = subprocess.check_output(['iw', 'dev'], universal_newlines=True)
        return [line.split()[1] for line in output.splitlines() if line.startswith('Interface')]
    except Exception as e:
        logging.error(f"Failed to list interfaces: {e}")
        return []

def get_current_mac(interface):
    """Get current MAC address for the given interface."""
    try:
        output = subprocess.check_output(['ip', 'link', 'show', interface], universal_newlines=True)
        for line in output.split('\n'):
            if 'link/ether' in line:
                return line.split('link/ether ')[1].split()[0]
        return None
    except Exception as e:
        logging.error(f"Failed to get MAC for {interface}: {e}")
        return None

def change_mac_address(interface, new_mac):
    """Change MAC address using ip & macchanger, with retries."""
    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            subprocess.check_call(['sudo', 'ip', 'link', 'set', interface, 'down'])
            subprocess.check_call(['sudo', 'macchanger', '-m', new_mac, interface])
            subprocess.check_call(['sudo', 'ip', 'link', 'set', interface, 'up'])
            logging.info(f"Changed MAC on {interface} to {new_mac}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Attempt {attempt}: Could not change MAC ({e})")
            time.sleep(2)
    logging.critical(f"Giving up changing MAC for {interface}")
    return False

def generate_new_mac_address(oui):
    """Generate MAC with specified OUI (format: xx:xx:xx:yy:yy:yy)."""
    rand = ''.join(random.choices('0123456789abcdef', k=6))
    return f"{oui}:{rand[:2]}:{rand[2:4]}:{rand[4:6]}"

def prompt_interface_choice(interfaces):
    print("\nAvailable network interfaces:")
    for i, iface in enumerate(interfaces, 1):
        print(f"{i}. {iface}")
    while True:
        try:
            idx = int(input("Select interface number: ").strip())
            if 1 <= idx <= len(interfaces):
                return interfaces[idx - 1]
            print("Invalid number. Try again.")
        except ValueError:
            print("Input must be a number.")

def prompt_mac_change(current_mac):
    while True:
        print("1. Generate new good MAC\n2. Enter custom MAC")
        choice = input("Select option (1/2): ").strip()
        if choice == '1':
            return generate_new_mac_address(random.choice(GOOD_OUIS))
        elif choice == '2':
            mac = input("Enter MAC (format: xx:xx:xx:xx:xx:xx): ").lower().strip()
            if validate_mac_address(mac):
                return mac
            print("Invalid MAC format.")
        else:
            print("Invalid choice.")

# Main Program
def main():
    setup_logging()
    check_prerequisites()

    while True:
        print("\n1. Create new operation directory\n2. Skip to changing MACs")
        choice = input("Select option (1/2): ").strip()
        if choice == '1':
            create_directory()
            break
        elif choice == '2':
            break
        else:
            print("Invalid choice.")

    interfaces = get_available_interfaces()
    if not interfaces:
        print("No interfaces found. Exiting.")
        logging.error("No interfaces found.")
        sys.exit(1)

    selected_iface = prompt_interface_choice(interfaces)
    current_mac = get_current_mac(selected_iface)
    if not current_mac:
        print(f"Could not get MAC for {selected_iface}")
        sys.exit(1)

    print(f"Current MAC ({selected_iface}): {current_mac}")
    status = check_mac_address(current_mac)
    print(f"Status: {status}")

    if status == 'BAD':
        new_mac = prompt_mac_change(current_mac)
        if change_mac_address(selected_iface, new_mac):
            print(f"MAC changed to: {new_mac}")
        else:
            print("Failed to change MAC after retries.")
    else:
        print("MAC is GOOD. No change needed.")

if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(f"[CRITICAL] {ex}")
        logging.critical(f"Fatal error: {ex}")
