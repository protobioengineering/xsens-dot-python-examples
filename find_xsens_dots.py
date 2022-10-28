'''
Find Xsens DOTs with Bluetooth LE scanner.

Scan for all Xsens DOTs in the area and print their addresses.
On Mac OS, addresses will be UUIDs (ex: ABCDEFGA-1111-2222-3333-444445555566)
rather than MAC addresses (ex: aa:bb:cc:12:34:56).

Requires Bleak (Bluetooth LE Agnostic Klient)
    - https://github.com/hbldh/bleak
    - https://bleak.readthedocs.io/en/latest/

Example output:
    $ python3 find_xsens_dots.py
    ABCDEFGA-1234-5678-9AAB-BCC112233445: Xsens DOT
    BCC11223-AABB-1234-1234-ABCDEFGABCDE: Xsens DOT
'''

import asyncio
from bleak import BleakScanner


async def main():
    devices = await BleakScanner.discover()
    xsens_dots = [dot for dot in devices if 'Xsens DOT' in str(dot)]
    if xsens_dots == None:
        print('No Xsens DOTs were found. Are the Xsens DOTs turned on?')
    else:
        print('Xsens DOTs found with the following addresses:')
        for dot in xsens_dots:
            print(dot)

if __name__ == "__main__":
    asyncio.run(main())
