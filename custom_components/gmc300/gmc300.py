import const
import serial
import struct

from . import const

v_device = None
v_device_opened = False

def open_device(port = None, baud_rate = 115200):
    global v_device, v_device_opened

    if port is None or port == '':
        port = const.DEFAULT_PORT

    try:
        v_device = serial.Serial(port, baudrate=baud_rate, timeout=1.0)
    except serial.serialutil.SerialException:
        print("ERROR: No device found")
        return -1

    v_device_opened = True
    clear_port()

    return 0



def clear_port():
    # close any pending previous command
    if v_device_opened: 
        v_device.write(">>")

        # get rid off all buffered data still in the queue
        while True:
            x = v_device.read(1)
            if x == '':
                break



def get_cpm(cpm_to_usievert=None):
    if not v_device_opened:
        print('ERROR: no device connected')
        return -1

    v_device.write('<GETCPM>>')
    cpm = v_device.read(2)

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



def convert_cpm_to_usievert(cpm, unit, cpm_to_usievert):
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
