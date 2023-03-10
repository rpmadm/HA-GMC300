import logging
from struct import pack, unpack
from collections import namedtuple
import time
from datetime import datetime, timedelta
import calendar
from abc import abstractmethod
from .const import *

_LOGGER = logging.getLogger(__name__)


class GMC300():

    m_device = None
    m_device_type = None
    m_device_name = DEFAULT_DEVICE_TYPE
    m_config = None
    m_config_data = None
    m_verbose = DEFAULT_VERBOSE_LEVEL
    m_terminate = False

    def __init__(self, model):
        _LOGGER.info(f"Geiger counter model: {model}")
        self.model = model
        self.model_code = self.get_model_code(model)
        if not self.model_code:
            raise SkyKettleError("Unknown kettle model")

    async def open_device(port=None, baud_rate=None, skip_check=False, device_type=None,
                    allow_fail=False):
        global m_device, m_device_name

        if port is None or port == '':
           port = DEFAULT_PORT

        if baud_rate is None or baud_rate == '':
           baud_rate = DEFAULT_BAUD_RATE      

        try:
           m_device = serial.Serial(port, baudrate=baud_rate, timeout=1.0)
        except serial.serialutil.SerialException:
           if not allow_fail:
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

    async def check_device_type():
        global m_device_type, m_device_name

        m_device_type = get_device_type()

        if m_device_type == '' or len(m_device_type) < 8:
            print("ERROR: device not found or supported")
            return -1

        m_device_name = m_device_type[:7]

        if m_device_name == 'GMC-280' or \
           m_device_name == 'GMC-300' or \
           m_device_name == 'GMC-320' or \
           m_device_name == 'GMC-500':
            if m_verbose == 2:
                print("device found: {}".format(m_device_type))

        elif m_device_name[:3] == 'GMC':
            print("WARNING: device found ({}) but officially not supported, using defaults"
                 .format(m_device_type))
            m_device_name = DEFAULT_DEVICE_TYPE

        else:
            print("ERROR: device not found or supported")
            return -1

        return 0
    
    async def clear_port():
        # close any pending previous command
        m_device.write(">>")

        # get rid off all buffered data still in the queue
        while True:
            x = m_device.read(1)
            if x == '':
                break

    async def command_returned_ok():
        ret = ''
        for loop in range(10):
            ret = m_device.read(1)
            if ret != '':
                break

        if ret == '' or ord(ret) != 0xaa:
            return False
        return True

    async def get_device_type():
        if m_device is None:
            print('ERROR: no device connected')
            return ''

        m_device.write('<GETVER>>')
        return m_device.read(14)

    async def get_serial_number():
        if m_device is None:
            print('ERROR: no device connected')
            return -1

        m_device.write('<GETSERIAL>>')
        serial_number = m_device.read(7)

        if serial_number == '' or len(serial_number) < 7:
            print('WARNING: no valid serial number received')
            return ''

        ser = ''
        for x in range(7):
            ser += '{:02X}'.format(ord(serial_number[x]))
        return ser

    async def set_power(on=True):
        if m_device is None:
            print('ERROR: no device connected')
            return -1

        if on:
            m_device.write('<POWERON>>')
            if m_verbose == 2:
                print('device power on')
        else:
            m_device.write('<POWEROFF>>')
            if m_verbose == 2:
                print('device power off')


    async def get_voltage():
        if m_device is None:
            print('ERROR: no device connected')
            return -1

        m_device.write('<GETVOLT>>')
        voltage = m_device.read(3)

        if voltage == '' or len(voltage) < 3:
            print('WARNING: no valid voltage received')
            return ''

        return '{} V'.format(voltage)


    async def get_cpm(cpm_to_usievert=None):
        if m_device is None:
            print('ERROR: no device connected')
            return -1

        m_device.write('<GETCPM>>')
        cpm = m_device.read(2)

        if cpm == '' or len(cpm) < 2:
            print('WARNING: no valid cpm received')
            return ''

        value = struct.unpack(">H", cpm)[0]

        unit_value = (value, 'CPM')
        if cpm_to_usievert is not None:
            unit_value = convert_cpm_to_usievert(value, 'CPM', cpm_to_usievert)

        if unit_value[1] == 'uSv/h':
            return '{:.4f} {:s}'.format(unit_value[0], unit_value[1])
        else:
            return '{:d} {:s}'.format(unit_value[0], unit_value[1])

    async def convert_cpm_to_usievert(cpm, unit, cpm_to_usievert):
        if cpm_to_usievert is None:
            return cpm, unit

        if unit == 'CPS':
            return cpm * cpm_to_usievert[1] / cpm_to_usievert[0] * 60, 'uSv/h'
        elif unit == 'CPM':
            return cpm * cpm_to_usievert[1] / cpm_to_usievert[0], 'uSv/h'
        elif unit == 'CPH':
            return cpm * cpm_to_usievert[1] / cpm_to_usievert[0] / 60, 'uSv/h'
        else:
            return cpm, unit

    async def reboot():
        if m_device is None:
            print('ERROR: no device connected')
            return -1

        m_device.write('<REBOOT>>')

    async def set_verbose_level(verbose):
        global m_verbose
        m_verbose = verbose


class GMCError(Exception):
    pass