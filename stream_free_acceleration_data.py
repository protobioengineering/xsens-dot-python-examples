'''
Turn on "measurement" service for Xsens DOT.

Turns on the Measurement service and sets the Payload mode (quaternion, Euler, etc.)
Characteristic/Service UUIDs and data encoding are available in
Xsens's "Xsens DOT BLE Services Specifications.pdf" document.

Requires Bleak (Bluetooth LE Agnostic Klient)
    - https://github.com/hbldh/bleak
    - https://bleak.readthedocs.io/en/latest/

Example output:
    $ python3 turn_on_measurement_service.py
    ...
    Short payload notification received.
        Sender: 15172004-4947-11e9-8646-d663bd873d93 (Handle: 42): Unknown
        Data: bytearray(b'\xd8\x05"D\xaf\x96@@k*\xa7@Z\xdd\x14\xc0\x00\x00\x00\x00')
        Encoded Free Acceleration: [(1143080408, 3.009197, 5.223928, -2.3260102, 0)]
    Short payload notification received.
        Sender: 15172004-4947-11e9-8646-d663bd873d93 (Handle: 42): Unknown
        Data: bytearray(b'\xf3F"D\r\xa5<@\x9c\x13\xa6@\xf0\x10\t\xc0\x00\x00\x00\x00')
        Encoded Free Acceleration: [(1143097075, 2.947574, 5.1898937, -2.1416588, 0)]
'''


import asyncio
import numpy as np
import sys

from bleak import BleakClient, BleakScanner


# Replace `address` with your Xsens DOT's address
address = 'ABCDEFGA-1111-2222-3333-444444555555'
short_payload_characteristic_uuid = '15172004-4947-11e9-8646-d663bd873d93'
measurement_characteristic_uuid = '15172001-4947-11e9-8646-d663bd873d93'

# For reference. Only "Free acceleration" is used in this example script.
payload_modes = {
    "High Fidelity (with mag)": [1, b'\x01'],
    "Extended (Quaternion)": [2, b'\x02'],
    "Complete (Quaternion)": [3, b'\x03'],
    "Orientation (Euler)": [4, b'\x04'],
    "Orientation (Quaternion)": [5, b'\x05'],
    "Free acceleration": [6, b'\x06'],
    "Extended (Euler)": [7, b'\x07'],
    "Complete (Euler)": [16, b'\x10'],
    "High Fidelity": [17, b'\x11'],
    "Delta quantities (with mag)": [18, b'\x12'],
    "Delta quantities": [19, b'\x13'],
    "Rate quantities (with mag)": [20, b'\x14'],
    "Rate quantities": [21, b'\x15'],
    "Custom mode 1": [22, b'\x16'],
    "Custom mode 2": [23, b'\x17'],
    "Custom mode 3": [24, b'\x18'],
    "Custom mode 4": [25, b'\x19'],
    "Custom mode 5": [26, b'\x1A'],
}

def encode_free_accel_bytes_to_string(bytes_):
    # These bytes are grouped according to Xsens's BLE specification doc
    data_segments = np.dtype([
        ('timestamp', np.uint32),
        ('x', np.float32),
        ('y', np.float32),
        ('z', np.float32),
        ('zero_padding', np.uint32)
        ])
    formatted_data = np.frombuffer(bytes_, dtype=data_segments)
    return formatted_data

def handle_short_payload_notification(sender, data):
    print('Short payload notification received.')
    print(f'\tSender: {sender}')
    print(f'\tData: {data}')
    print(f'\tEncoded Free Acceleration: {encode_free_accel_bytes_to_string(data)}')


async def main(ble_address):
    print(f'Looking for Bluetooth LE device at address `{ble_address}`...')
    device = await BleakScanner.find_device_by_address(ble_address, timeout=20.0)
    if(device == None):
        print(f'A Bluetooth LE device with the address `{ble_address}` was not found.')
    else:
        print(f'Client found at address: {ble_address}')
        print(f'Connecting...')

        # This `async` block starts and keeps the Bluetooth LE device connection.
        # Once the `async` block exits, the BLE device automatically disconnects.
        async with BleakClient(device) as client:
            print(f'Client connection = {client.is_connected}')

            '''
            Turn on notification for a "short payload" (UUID: 0x2004). A measurement mode
            will have either a short, medium, or long payload. Each payload needs to be
            turned on separately (i.e. write an enable message to a payload's characteristic UUID)
            '''
            print(f'Turning on Short Payload notification at `{short_payload_characteristic_uuid}`...')
            await client.start_notify(short_payload_characteristic_uuid, handle_short_payload_notification)
            print('Notifications turned on.')

            '''
            Turn on the Measurement characteristic
            '''
            payload_mode_values = payload_modes["Free acceleration"]
            payload_mode = payload_mode_values[1] # is in b'\x00' format
            measurement_default = b'\x01' # This apparently never changes
            start_measurement = b'\x01' # 01 = start, 00 = stop
            full_turnon_payload = measurement_default + start_measurement + payload_mode # b'\x01\x01\x06'
            print(f'Setting payload with binary: {full_turnon_payload}')
            write = await client.write_gatt_char(measurement_characteristic_uuid, full_turnon_payload, True)
            print(f'Streaming turned on.')
            await asyncio.sleep(1.0) # How long to stream data for
            print(f'Streaming turned off.')

        print(f'Disconnected from `{ble_address}`')

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) == 2 else address))