import serial
import sys


READ_SPEED = 9600


class SerialAPI:
    __port: serial.Serial = None
    __blocked: bool = True

    @classmethod
    def flush(cls):
        cls.__port.flush()
        cls.__port.flushInput()
        cls.__port.flushOutput()

    @classmethod
    def usePort(cls, port_name: str) -> int:
        if cls.__port:
            cls.__port.close()

        try:
            port = serial.Serial(port_name, READ_SPEED)

            cls.__port = port
            cls.__blocked = False
            return 0

        except serial.SerialException:
            cls.__blocked = True
            return 1

    @classmethod
    def sendLine(cls, line):
        if not cls.__port or cls.__blocked:
            return
        cls.__port.write( bytearray(line, "utf-8") )

    @classmethod
    def disable(cls) -> None:
        __blocked = True

    @classmethod
    def isDisabled(cls):
        return cls.__blocked


def get_serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(32)]
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException) as e:
            if e.args[0].find("PermissionError") > 0:
                print(e)

    return result
