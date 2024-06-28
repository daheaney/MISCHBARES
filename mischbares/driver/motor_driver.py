import serial
import time
import sys

class motorError(Exception):
    """Custom exception class for motor-related errors"""
    pass

class SerialConnection:
    def __init__(self, port, baudrate, timeout):
        """ Initializes the serial connection"""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
        except serial.SerialException:
            print('Unable to connect to the motor or motor is already connected. Check the com port and try again.')
            sys.exit(1)  # Exiting the program if the motor is not connected.

    def close(self):
        """ Closes the serial connection"""
        self.ser.close()

    def send_command(self, command):
        """ Sends a command to the serial connection
          Args:
            command (str): The command to send to the serial connection.
          """
        self.ser.write((command + "\n").encode('utf-8'))

    def read_response(self):
        """ Reads and returns the response from the serial connection

         Returns:
            str: The response from the serial connection."""
        return self.ser.readline().decode('utf-8').strip()


class Motor:
    def __init__(self, connection, num):
        """ Initializes a motor with a given serial connection and motor number"""
        self.connection = connection
        self.num = num

    def check_connection(self):
        """ Checks if the motor is connected
         Returns:
            bool: True if the motor is connected, False otherwise.
        """
        self.connection.send_command(str(self.num) + "Q")
        response = self.connection.read_response()
        if response == 'MOTOR_CONNECTED':
            return True
        else:
            return False

    def set_speed(self, speed):
        """ Sets the speed of the motor
         Args:
            speed (int): The speed to set the motor to. Must be between 0 and 1000.
        """
        if 0 < speed < 1000:
            self.connection.send_command(str(self.num) + "V" + str(speed))
        else:
            raise motorError('Speed must be between 0 and 1000')

    def stop(self):
        """ Stops the motor"""
        self.connection.send_command(str(self.num) + "S")

    def set_acceleration(self, acceleration):
        """ Sets the acceleration of the motor

         Args:
            acceleration (int): The acceleration to set the motor to. Must be between 0 and 1000.
        """
        if 0 < acceleration < 1000:
            self.connection.send_command(str(self.num) + "A" + str(acceleration))
        else:
            raise motorError('Acceleration must be between 0 and 1000')

    def move(self, steps, wait_for_motor=True):
        """ Moves the motor clockwise at the current speed for a set number of steps
         Args:
            steps (int): The number of steps to move the motor.
            wait_for_motor (bool, optional): Whether to wait for the motor to finish moving. Defaults to True.
        """
        self.connection.send_command(str(self.num) + "F" + str(steps))
        if wait_for_motor:
            self.wait_for_motor()

    def wait_for_motor(self):
        """ Wait for acknowledgment from the motor that task is finished"""
        while True:
            response = self.connection.read_response()
            if response == 'MOTOR_FINISHED':
                break

#Should we remove the moveUp and moveDown methods since they are just copies of the move method?

    def moveUp(self, steps, wait_for_motor=True):
        """ Moves the motor clockwise at the current speed for a set number of steps
         Args:
            steps (int): The number of steps to move the motor.
            wait_for_motor (bool, optional): Whether to wait for the motor to finish moving. Defaults to True.
        """
        self.connection.send_command(str(self.num) + "F" + str(steps))
        if wait_for_motor:
            self.wait_for_motor()

    def moveDown(self, steps, wait_for_motor=True):
        """ Moves the motor clockwise at the current speed for a set number of steps
         Args:
            steps (int): The number of steps to move the motor.
            wait_for_motor (bool, optional): Whether to wait for the motor to finish moving. Defaults to True.
        """
        self.connection.send_command(str(self.num) + "F-" + str(steps))
        if wait_for_motor:
            self.wait_for_motor()
