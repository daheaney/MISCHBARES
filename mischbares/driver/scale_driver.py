from collections import namedtuple
import serial
import sys

CMD_PRINT = b"P"
CMD_TARA = b"T"

CMD_EXPCLICIT_TARA = b"U"
CMD_EXPCLICIT_NULL = b"V"

CMD_INFO_TYPE = b"x1_"
CMD_INFO_SNR = b"x2_"
CMD_INFO_VERSION_SCALE = b"x3_"
CMD_INFO_VERSION_CONTROL_UNIT = b"x4_"
CMD_INFO_USER = b"x5_"

CMD_FILTER_ENVIRONMENT_VERY_STABLE = b"K"
CMD_FILTER_ENVIRONMENT_STABLE = b"L"
CMD_FILTER_ENVIRONMENT_UNSTABLE = b"M"
CMD_FILTER_ENVIRONMENT_VERAY_UNSTABLE = b"N"

CMD_KEYBOARD_LOCK = b"O"
CMD_KEYBOARD_UNKLOCK = b"R"
CMD_KEYPRESS_PRINT = b"kP_"
CMD_KEYPRESS_CANCEL = b"s3_"

CMD_BEEP = b"Q"

CMD_RESTART = b"S"
CMD_ADJUST_INTERNAL = b"Z"
CMD_ADJUST_EXTERNAL = b"W"


ESC = chr(27).encode("utf-8")
CR = chr(13).encode("utf-8")
LF = chr(10).encode("utf-8")


Measurement = namedtuple(
    "Measurement", ["mode", "value", "unit", "stable", "message"],
)


class Scale:

    encoding = "utf-8"

    def __init__(self, conf, baud, timeout):
        """Initialization for the class"""

        self.conf = conf
        self.baud = baud
        self.timeout = timeout
        try: 
            self.ser = serial.Serial(conf, baud, timeout=timeout)
        except serial.SerialException:
            print('Unable to connect to the scale or scale is already connected. Check the com port and try again.')
            #sys.exit(1) #Exiting the program if the scale is not connected.

    def connect(self):
        """Establishes a new serial connection"""
        if self.ser is None:
            self.ser = serial.Serial(*self._serial_args, **self._serial_kargs)

    def open(self):
        """Establishes a new serial connection

        This function just calls the 'connect()' method and is here for
        compability with other libraries that use open() / close().
        """
        self.connect()

    def close(self):
        """Closes a serial connection, if one is open"""
        if self.ser:
            self.ser.close()
            self.ser = None

    def send(self, command):
        """Sends a command to the scale
        Args:
            command (bytes): The command to send to the scale.
        """
        if not isinstance(command, bytes):
            command = str(command).encode(self.encoding)
        self.ser.write(ESC + command + CR + LF)

    def read(self, nr_of_bytes=1):
        """Reads some number of bytes from the serial connection
        Args:
            nr_of_bytes (int, optional): The number of bytes to read. The default is 1.
        Returns:
            bytes: The bytes read from the serial connection.
        """
        return self.ser.read(nr_of_bytes)
    
    def tare(self):
        """Waits for a stable measurment then it tares the scale"""
        while True:
            self.send(CMD_TARA)
            measurement = self.measure_stable()
            if measurement.value == 0:
                break
            else:
                continue

    def readline(self):
        """Reads bytes from the serial connection until a newline
        Returns:
            bytes: The bytes read from the serial connection.
        """
        return self.ser.readline()

    def readlines(self):
        """Reads the output from the scale and decodes it
        Returns:
            list: A list of lines of available data.
        """
        lines = []
        i = 0
        for i in range(1):
            i += 1
            line = self.readline()
            line = line.decode(self.encoding)
            if not line.strip():
                # a line with only whitespace shows the end of the output
                # also a read timeout produces b''
                break
            lines.append(line)
        return lines


    def get(self, command):
        """Sends a command and returns the available data
        Args:
           command (bytes): The command to send to the scale.
        Returns:
            list: A list of decoded lines sent from the scale.
        """
        self.send(command)
        return self.readlines()

    def measure(self):
        """Sends a print
        Returns:
            Measurement: A namedtuple with the measurement data including the mode, value, unit, stable, and message.
        """
        raw_data_lines = self.get(CMD_PRINT)
        if raw_data_lines:
            raw_data = raw_data_lines[0]
            return parse_measurement(raw_data)
        else:
            # propably serial connection timeout
            return Measurement(None, None, None, None, "Connection Timeout")
    
    def measure_stable(self):   
        """Waits for a stable measurement
        Returns:
            Measurement: A namedtuple with the measurement data including the mode, value, unit, stable, and message.
        """
        while True:  
            measurement = self.measure() 
            
            if measurement.stable: 
                #print(str(measurement))
                return measurement  

        
    def __enter__(self):
        """Context manager: establishes connection
        Returns:
           Scale: The object itself.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Context manager: closes connection 
        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
        """
        self.close()


def parse_measurement(raw_data):
    """Parses the raw data from a measurement
    Args:
        raw_data (str): The raw data from the scale.
    Returns:
        Measurement: A namedtuple with the measurement data including the mode, value, unit, stable, and message.
    """
    if len(raw_data) <= 16:
        return _parse_16_char_output(raw_data)
    else:
        return _parse_22_char_output(raw_data)


def _parse_22_char_output(raw_data):
    """Parse a 16 character measurement output

    The scale can be set to return two different types of output. This
    function parses a 16 character output.

    Returns:
        Measurement: A namedtuple with the measurement data including the mode, value, unit, stable, and message.
    """

    mode = raw_data[:6].strip()
    rest = raw_data[6:]

    return _parse_16_char_output(rest, mode)


def _parse_16_char_output(raw_data, mode="unknown"):
    """ parse a 16 character measurement output

    The scale can be set to return two different types of output. This
    function parses a 16 character output.

    Args:  
        raw_data (str): The raw data from the scale.
        mode (str): The mode of the measurement. Default is "unknown".
    Returns:
        Measurement: A namedtuple with the measurement data including the mode, value, unit, stable, and message.
    """

    if _is_message(raw_data):
        msg = raw_data.strip()
        return Measurement(None, None, None, None, msg)

    raw_data = _remove_calibration_note(raw_data)

    sign = raw_data[0].strip()
    value_and_unit = raw_data[1:].strip()
    parts = value_and_unit.rsplit(" ", 1)
    raw_value = parts[0]
    value = float(sign + "".join(raw_value.split()))

    if len(parts) == 2:
        unit = parts[1]
        stable = True
    else:
        unit = None
        stable = False

    return Measurement(mode, value, unit, stable, None)



def _is_message(raw_data):
    """If the scale sends a message including "high", "low", "cal", "err", "--" it will return True else it will return False.
    Args:
        raw_data (str): The raw data from the scale.
    Returns:
        bool: True if the scale sends a message, False otherwise.
    """
    for identifier in ("high", "low", "cal", "err", "--"):
        if identifier in raw_data.lower():
            return True
    return False


def _remove_calibration_note(raw_data):
    """Adjusts the raw data string if a calibration note is present

    According to the manual, this should not happen in SBI mode of the
    scale. This is included to prevent hiccups but probably not handled
    the right way....

    The data with a calibration node on in put and output of this method

    in:  "+123.4567[8]g  "
    out: "+123.45678  g  "
    
    Args:
        raw_data (str): The raw data from the scale.
    Returns:
        str: The raw data without the calibration note.
    """
    if "[" in raw_data:
        raw_data = raw_data.replace("[", "").replace("]", "  ")
    return raw_data
