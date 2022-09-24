import serial
import struct
import binascii
import time

import . const

import logging
from homeassistant.core import HomeAssistant








def clear_port():
    # close any pending previous command
    m_device.write(">>")

    # get rid off all buffered data still in the queue
    while True:
        x = m_device.read(1)
        if x == '':
            break


def open_device(port=None, baud_rate=115200, skip_check=False, device_type=None,
                allow_fail=False):
    global m_device, m_device_name

    if port is None or port == '':
        port = DEFAULT_PORT

    try:
        m_device = serial.Serial(port, baudrate=baud_rate, timeout=1.0)
    except serial.serialutil.SerialException:
        if not allow_fail:
            if platform.system() == 'Windows':
                print("ERROR: No device found (use the '-p COM1' option and provide the correct port)")
            else:
                print("ERROR: No device found (use the '-p /dev/ttyUSB0' option and provide the correct port, or install the udev rule as described in the INSTALL file)")
        return -1

    clear_port()

    res = 0
    if not skip_check:
        res = check_device_type()

    if device_type is not None:
        if device_type == 'GMC-280' or \
           device_type == 'GMC-300' or \
           device_type == 'GMC-320' or \
           device_type == 'GMC-500':
            m_device_name = device_type
            if m_verbose == 2:
                print("using device-type: {}".format(m_device_name))
        else:
            print("WARNING: unsupported selected device type '{}', defaulting to '{}'"
                  .format(device_type, m_device_name))

    return res
