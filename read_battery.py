'''
Read "battery" characteristic from Xsens DOT.

Characteristic/Service UUIDs and data encoding are available in
Xsens's "Xsens DOT BLE Services Specifications.pdf" document.

Requires Bleak (Bluetooth LE Agnostic Klient)
    - https://github.com/hbldh/bleak
    - https://bleak.readthedocs.io/en/latest/
'''


import asyncio
import numpy as np
import sys

from bleak import BleakClient, BleakScanner
from charset_normalizer import from_bytes, detect


address = 'ABCDEFGA-1111-2222-3333-444444555555'
battery_characteristic_uuid = '15173001-4947-11e9-8646-d663bd873d93'


def encode_bytes_to_string(bytes_):
    # These bytes are grouped according to Xsens's BLE specification doc
    data_segments = np.dtype([
        ('battery_level', np.uint8),
        ('is_charging', np.uint8)
        ])
    formatted_data = np.frombuffer(bytes_, dtype=data_segments)
    return formatted_data


async def main(ble_address):
    print(f'Looking for Bluetooth LE device at address `{ble_address}`...')
    device = await BleakScanner.find_device_by_address(ble_address, timeout=20.0)
    if(device == None):
        print(f'A Bluetooth LE device with the address `{ble_address}` was not found.')
    else:
        print(f'Client found at address: {ble_address}')
        print(f'Connecting...')

        # This `async` block starts and keeps the Bluetooth LE device connection.
        # Once the `async` block exits, BLE device automatically disconnects.
        async with BleakClient(device) as client:
            print(f'Client connection = {client.is_connected}')
            print(f'Reading characteristic at `{battery_characteristic_uuid}`...')
            device_info = await client.read_gatt_char(battery_characteristic_uuid)
            encoded_device_info = encode_bytes_to_string(device_info)
            print(f'Raw device info: {device_info}')
            print(f'Encoded Device info: {encoded_device_info}')

            battery_level = encoded_device_info["battery_level"][0]
            print(f'Battery level: {battery_level}%')

            device_is_charging = "Yes" if encoded_device_info["is_charging"] == 1 else "No"
            print(f'Device is charging: {device_is_charging}')

        print(f'Disconnected from `{ble_address}`')

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) == 2 else address))