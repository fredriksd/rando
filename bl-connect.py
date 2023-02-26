#! /usr/bin/env python

import argparse
import re
import subprocess
import sys

WH_1000_XM3 = "WH-1000XM3"
LE_WH_1000_XM3 = "LE_WH-1000XM3"

NUMBER_OF_CONNECTION_ATTEMPTS = 5

def get_args():
    parser = argparse.ArgumentParser(
            prog = "bl-connect",
            description = "Handle connection to bluetooth devices."
            )
    parser.add_argument("--disconnect",
                        action = "store_true",
                        default = False,
                        help = "Disconnect from device.")

    return parser.parse_args()

def get_mac_address(bluetooth_entry: str):
    mac_address_regex = re.compile("([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})")
    mac_address_search = mac_address_regex.search(bluetooth_entry)
    return mac_address_search.group()

def get_list_of_bluetooth_devices() -> str:
    args = ["bluetoothctl", "devices"]
    bluetooth_devices_cmd = subprocess.run(args, capture_output = True)

    if bluetooth_devices_cmd.returncode != 0:
        raise RuntimeError(f"Failed to get bluetooth devices:"
                           f"{bluetooth_devices_cmd.stderr}")
    return bluetooth_devices_cmd.stdout.decode("utf-8").split("\n")

def connect(mac_address: str) -> subprocess.CompletedProcess:
    args = ["bluetoothctl", "--timeout", "5", "connect", mac_address]
    bluetooth_connect_cmd = subprocess.run(args, capture_output = True)

    return bluetooth_connect_cmd

def attempt_connect(mac_address: str, attempts: int) -> int:
    for i in range(1, NUMBER_OF_CONNECTION_ATTEMPTS):
        print(f"\rAttempting to connect to {mac_address}, attempt {i} out of "
              f"{NUMBER_OF_CONNECTION_ATTEMPTS}", end = "")
        cmd = connect(mac_address)
        stdout = cmd.stdout.decode("utf-8")
        returncode = cmd.returncode

        new_transport_regex = re.compile("\[.*NEW.*\] Transport /org/bluez/.*")

        if returncode == 0 and new_transport_regex.search(stdout) != None:
            print()
            return i
            
    print()
    raise RuntimeError(f"Failed to connect to {mac_address} after "
                       f"{NUMBER_OF_CONNECTION_ATTEMPTS} attempts")

def disconnect():
    args = ["bluetoothctl", "disconnect"]
    subprocess.run(args)

def main():
    try:
        args = get_args()

        if args.disconnect:
            returncode = disconnect()
            return returncode

        bluetooth_devices = get_list_of_bluetooth_devices() 
        for entry in bluetooth_devices:
            if WH_1000_XM3 in entry or LE_WH_1000_XM3 in entry:
                mac_address = get_mac_address(entry)
                
                attempts = attempt_connect(mac_address, NUMBER_OF_CONNECTION_ATTEMPTS)
                print(f"Successfully connected to {mac_address}")
                print(f"Number of tries: {attempts} out of "
                      f"{NUMBER_OF_CONNECTION_ATTEMPTS} allowed tries")
    
    except Exception as e:
        print("Error: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
