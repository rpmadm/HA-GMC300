import serial
import struct
import binascii
import time
import logging
import platform
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = '/dev/ttyUSB-geiger'  # try '/dev/ttyUSB0' without udev rules
DEFAULT_BAUD_RATE = 115200
DEFAULT_CPM_TO_SIEVERT = '1000,6.50'
DEFAULT_OUTPUT_IN_CPM = False
DEFAULT_NO_PARSE = False
DEFAULT_SKIP_CHECK = False
DEFAULT_UNIT_CONVERSION_FROM_DEVICE = False
DEFAULT_DEVICE_TYPE = None
DEFAULT_FLASH_SIZE = 0x00100000  # 1 MByte
DEFAULT_CONFIGURATION_SIZE = 0x100  # 256 byte
DEFAULT_VERBOSE_LEVEL = 2

gmc_device = None
gmc_device_type = None
gmc_device_name = DEFAULT_DEVICE_TYPE
m_config = None
m_config_data = None
gmc_verbose = DEFAULT_VERBOSE_LEVEL
m_terminate = False

class GMC:
#Общий класс интеграции, используется для инициализации, а так же как объект хранящий информацию обо всех устройствах интеграции
    def __init__(self, hass: HomeAssistant) -> None:
        self.devices = []


     #   def pull_data(self):
		# Метод получения информации из API и создания объектов и сохранение их в массив self.devices  на основе этой информации,  
        # специально вынесен из конструктора в отдельный метод из-за ограничений HA на вызов запросов в не асинхронных методах. 
        # В моем случае я вызывал методы API с помощью модуля request, парсил с помощью json, 
        # затем передавал нужную информацию в конструктор класса устройства.



    #gmc_device = serial.Serial( "/dev/ttyUSB-geiger", 57600 )

    def set_verbose_level(verbose):
        global gmc_verbose
        gmc_verbose = verbose


    def gmc_clear_port():
    # close any pending previous command
        gmc_device.write(">>")

        # get rid off all buffered data still in the queue
        while True:
            x = gmc_device.read(1)
            if x == '':
                break

    def command_returned_ok():
        ret = ''
        for loop in range(10):
            ret = gmc_device.read(1)
            if ret != '':
                break

        if ret == '' or ord(ret) != 0xaa:
            return False
        return True

    # Получить тип устройства
    def gmc_get_devtype():
        if gmc_device is None:
            print('ERROR: no device connected')
            return ''

        gmc_device.write('<GETVER>>')
        return gmc_device.read(14)

    # Определить тип обнруженного устройства
    def gmc_chk_devtype():
        global gmc_device_type, gmc_device_name

        gmc_device_type = gmc_get_devtype()

        if gmc_device_type == '' or len(gmc_device_type) < 8:
            print("ERROR: device not found or supported")
            return -1

        gmc_device_name = gmc_device_type[:7]

        if gmc_device_name == 'GMC-280' or \
            gmc_device_name == 'GMC-300' or \
            gmc_device_name == 'GMC-320' or \
            gmc_device_name == 'GMC-500':
            if gmc_verbose == 2:
                print("device found: {}".format(gmc_device_type))

        elif gmc_device_name[:3] == 'GMC':
            print("WARNING: device found ({}) but officially not supported, using defaults"
                  .format(gmc_device_type))
            gmc_device_name = DEFAULT_DEVICE_TYPE

        else:
            print("ERROR: device not found or supported")
            return -1

        return 0

    # Получить серийный номер устройства
    def gmc_get_serial():
        if gmc_device is None:
            print('ERROR: no device connected')
            return -1

        gmc_device.write('<GETSERIAL>>')
        serial_number = gmc_device.read(7)

        if serial_number == '' or len(serial_number) < 7:
            print('WARNING: no valid serial number received')
            return ''

        ser = ''
        for x in range(7):
            ser += '{:02X}'.format(ord(serial_number[x]))
        return ser

    # Включить питание
    def gmc_set_power(on=True):
        if gmc_device is None:
            print('ERROR: no device connected')
            return -1

        if on:
            gmc_device.write('<POWERON>>')
            if gmc_verbose == 2:
                print('device power on')
        else:
            gmc_device.write('<POWEROFF>>')
            if gmc_verbose == 2:
                print('device power off')

    # Получить напряжение питания
    def get_voltage():
        if gmc_device is None:
            print('ERROR: no device connected')
            return -1

        gmc_device.write('<GETVOLT>>')
        gmc_voltage = gmc_device.read(3)

        if gmc_voltage == '' or len(gmc_voltage) < 3:
            print('WARNING: no valid voltage received')
            return ''

        return '{} V'.format(gmc_voltage)

    # Получить значение датчика радиации
    def get_cpm(cpm_to_usievert=None):
        if gmc_device is None:
            print('ERROR: no device connected')
            return -1

        gmc_device.write('<GETCPM>>')
        gmc_cpm = gmc_device.read(2)

        if gmc_cpm == '' or len(gmc_cpm) < 2:
            print('WARNING: no valid cpm received')
            return ''

        gmc_value = struct.unpack(">H", gmc_cpm)[0]

        unit_value = (gmc_value, 'CPM')
        if cpm_to_usievert is not None:
            unit_value = convert_cpm_to_usievert(gmc_value, 'CPM', cpm_to_usievert)

        if unit_value[1] == 'uSv/h':
            return '{:.4f} {:s}'.format(unit_value[0], unit_value[1])
        else:
            return '{:d} {:s}'.format(unit_value[0], unit_value[1])

    # Перевод единиц измерения
    def convert_cpm_to_usievert(cpm, unit, cpm_to_usievert):
        if cpm_to_usievert is None:
            return cpm, unit

        if unit == 'CPS':
            return cpm * cpm_to_usievert[1] / cpm_to_usievert[0] * 60, 'мкЗв/ч'
        elif unit == 'CPM':
            return cpm * cpm_to_usievert[1] / cpm_to_usievert[0], 'мкЗв/ч'
        elif unit == 'CPH':
            return cpm * cpm_to_usievert[1] / cpm_to_usievert[0] / 60, 'мкЗв/ч'
        else:
            return cpm, unit
 

    # Получить температуру
    def get_temperature():
        if gmc_device is None:
            print('ERROR: no device connected')
            return -1

        gmc_device.write('<GETTEMP>>')
        temp = gmc_device.read(4)

        if temp == '' or len(temp) < 4:
            print('WARNING: no valid temperature received')
            return ''

        sign = ''
        if ord(temp[2]) != 0:
            sign = '-'
        temp_str = u'{:s}{:d}.{:d} {:s}{:s}' \
               .format(sign, ord(temp[0]), ord(temp[1]), chr(0x00B0), chr(0x0043))
        return temp_str.encode('utf-8')

    # Получить дату/время 
    def get_date_and_time():
        if gmc_device is None:
            print('ERROR: no device connected')
            return -1

        gmc_device.write('<GETDATETIME>>')
        date = gmc_device.read(7)

        if date == '' or len(date) < 7:
            print('WARNING: no valid date received')
            return ''

        (year, month, day, hour, minute, second, dummy) = struct.unpack(">BBBBBBB", date)
        return "{}/{}/{} {}:{}:{}".format(year, month, day, hour, minute, second)

    # Установить дату/время
    def set_date_and_time(date_time):
        if gmc_device is None:
            print('ERROR: no device connected')
            return -1

        cmd = struct.pack('>BBBBBB',
                          date_time.year - 2000,
                          date_time.month,
                          date_time.day,
                          date_time.hour,
                          date_time.minute,
                          date_time.second)
        gmc_device.write('<SETDATETIME' + cmd + '>>')

        if not command_returned_ok():
            print("WARNING: setting date and time not succeded")

    # Перезагрузить устройство
    def reboot():
        if gmc_device is None:
            print('ERROR: no device connected')
            return -1

        gmc_device.write('<REBOOT>>')

    # Открыть устройство
    def open_device(port=None, baud_rate=115200, skip_check=False, device_type=None,
                    allow_fail=False):
        global gmc_device, gmc_device_name

        if port is None or port == '':
            port = DEFAULT_PORT

        try:
            gmc_device = serial.Serial(port, baudrate=baud_rate, timeout=1.0)
        except serial.serialutil.SerialException:
            if not allow_fail:
                if platform.system() == 'Windows':
                    print("ERROR: No device found (use the '-p COM1' option and provide the correct port)")
                else:
                    print("ERROR: No device found (use the '-p /dev/ttyUSB0' option and provide the correct port, or install the udev rule as described in the INSTALL file)")
            return -1

        gmc_clear_port()

        res = 0
        if not skip_check:
            res = gmc_chk_devtype()

        if gmc_device_type is not None:
            if gmc_device_type == 'GMC-280' or \
                gmc_device_type == 'GMC-300' or \
                gmc_device_type == 'GMC-320' or \
                gmc_device_type == 'GMC-500':
                gmc_device_name = gmc_device_type
            if gmc_verbose == 2:
                print("using device-type: {}".format(gmc_device_name))
        else:
            print("WARNING: unsupported selected device type '{}', defaulting to '{}'"
                  .format(gmc_device_type, gmc_device_name))

        return res


