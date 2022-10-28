'''
Read "measurement" service from Xsens DOT.

Reads whether the measurement service for a DOT is set to on or off.

Characteristic/Service UUIDs and data encoding are available in
Xsens's "Xsens DOT BLE Services Specifications.pdf" document.

Requires Bleak (Bluetooth LE Agnostic Klient)
    - https://github.com/hbldh/bleak
    - https://bleak.readthedocs.io/en/latest/

Example output:
    $ python3 read_state_of_measurement_service.py
    Looking for Bluetooth LE device at address `ABCDEFGA-1111-2222-3333-444444555555`...
    Client found at address: ABCDEFGA-1111-2222-3333-444444555555
    Connecting...
    Client connection = True
    Reading characteristic at `15172001-4947-11e9-8646-d663bd873d93`...
    Raw device info: bytearray(b'\x01\x00\x04')
    Encoded Device info: [(1, 0, 4)]
    Measurement type: 1
    Started or stopped: Stopped
    Payload type: 4
    See `Xsens DOT BLE Service Specifications` doc to correlate numbers to measurement modes.
    Disconnected from `ABCDEFGA-1111-2222-3333-444444555555`
'''


import asyncio
import numpy as np
import sys

from bleak import BleakClient, BleakScanner


# Replace `address` with your Xsens DOT's address
address = 'ABCDEFGA-1111-2222-3333-444444555555'
measurement_characteristic_uuid = '15172001-4947-11e9-8646-d663bd873d93'


def encode_bytes_to_string(bytes_):
    # These bytes are grouped according to Xsens's BLE specification doc
    data_segments = np.dtype([
        ('a', np.uint8),
        ('b', np.uint8),
        ('c', np.uint8)
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
            print(f'Reading characteristic at `{measurement_characteristic_uuid}`...')
            device_info = await client.read_gatt_char(measurement_characteristic_uuid)
            encoded_device_info = encode_bytes_to_string(device_info)
            print(f'Raw device info: {device_info}')
            print(f'Encoded Device info: {encoded_device_info}')

            measurement_type = encoded_device_info["a"][0]
            state = encoded_device_info["b"][0]
            payload_type = encoded_device_info["c"][0]

            start_or_stop = 'Started' if state == 1 else 'Stopped'
            print(f'Measurement type: {measurement_type}')
            print(f'Started or stopped: {start_or_stop}')
            print(f'Payload type: {payload_type}')
            print('See `Xsens DOT BLE Service Specifications` doc to correlate numbers to measurement modes.')

        print(f'Disconnected from `{ble_address}`')

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) == 2 else address))