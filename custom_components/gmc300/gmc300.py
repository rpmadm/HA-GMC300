import serial
import struct
import logging
import time

from . import const

gmc_logger = logging.getLogger(__name__)
gmc_logger.setLevel(logging.DEBUG)

v_device = None
v_device_opened = False

def open_device(port = None, baud_rate = 115200):
    global v_device, v_device_opened

    gmc_logger.debug("INFO: Вход в процедуру подключения")

    if port is None or port == '':
        port = const.DEFAULT_PORT

    gmc_logger.debug("INFO: Выбран порт " + port)

    try:
        v_device = serial.Serial(port, baudrate=baud_rate, timeout=1.0)
        gmc_logger.debug("INFO: Подключено устройство")
    except serial.serialutil.SerialException:
        gmc_logger.debug("ERROR: Не найдено устройство")
        return -1

    v_device_opened = True
    clear_port()

    gmc_logger.debug("SUCCESS: Устройство доступно")
    return 0
#


def clear_port():
    # close any pending previous command
    if v_device_opened: 
        v_device.write(str.encode(">>"))

        # get rid off all buffered data still in the queue
        while True:
            x = v_device.read(1)
            if x == '':
                break



def get_cpm():
    ret_value = 0
    
    get_version()

    gmc_logger.debug("INFO: Начальное значение value = " + str(ret_value))
    if not v_device_opened:
        gmc_logger.debug("ERROR: Нет подключения к устройству")
        return -1

    v_device.write(str.encode('<GETCPM>>'))

    if v_device.in_waiting > 0:
        cpm = v_device.read(2)

        gmc_logger.debug('INFO: Сырое значение cpm ' + cpm)

#        if cpm == '' or len(cpm) < 2:
#            gmc_logger.debug('WARNING: Нет корректного значения cpm')
#            return -100
#        else:
            
        ret_value = struct.unpack(">H", cpm)[0]
        gmc_logger.debug("INFO: Конечное значение value = " + str(ret_value))
        
        return ret_value 
    
    
    #    time.sleep(2)
    #    unit_value = (value, 'CPM')

    #    if cpm_to_usievert is not None:
    #        unit_value = convert_cpm_to_usievert(value, 'CPM', cpm_to_usievert)

    #    if unit_value[1] == 'uSv/h':
    #        return '{:.4f} {:s}'.format(unit_value[0], unit_value[1])
    #    else:
    #        return '{:d} {:s}'.format(unit_value[0], unit_value[1])
    


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


def get_version():
    global v_device
    
    v_device.write(str.encode("<GETVER>>"))
    v_version = v_device.read(14)

    gmc_logger.debug("INFO: Версия ПО:" + str(v_version))
    
    return v_version