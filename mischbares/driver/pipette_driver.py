import logging
import serial
import time

PRE = bytes([0x01])
POST = bytes([0x0d]) # or POST = str.encode('\r') 
ADR = '1'
BAUD = '5'

ERROR_CODES = {
    "err_codes" :	[str.encode("er1"), str.encode("er2"), str.encode("er3"), str.encode("er4")]
}

REGULAR_COMMANDS = {
    'SET_ADR'  	  	 		: [str.encode("A")  + str.encode(ADR),  str.encode("ok")],
    'BAUD_9600'   	 		: [str.encode("B")  + str.encode('0'),  str.encode("ok")],
    'BAUD_19200'  	 		: [str.encode("B")  + str.encode('1'),  str.encode("ok")],
    'BAUD_115200' 	 		: [str.encode("B")  + str.encode('5'),  str.encode("ok")],
    'DISABLE_LRC' 	 		: [str.encode("C")  + str.encode('0'),  str.encode("ok")],
    'ENABLE_LRC'  	 		: [str.encode("C")  + str.encode('1'),  str.encode("ok")],
    'INITIALIZE'  	 		: [str.encode("RZ") + str.encode('1'),  str.encode("ok")],
    'RESET'  	 		    : [str.encode("RZ") + str.encode('30'), str.encode("ok")],
    'INWARD_SPEED_1' 		: [str.encode("SI") + str.encode('1'),  str.encode("ok")],
    'INWARD_SPEED_2' 		: [str.encode("SI") + str.encode('2'),  str.encode("ok")],
    'INWARD_SPEED_3' 		: [str.encode("SI") + str.encode('3'),  str.encode("ok")],
    'INWARD_SPEED_4' 		: [str.encode("SI") + str.encode('4'),  str.encode("ok")],
    'INWARD_SPEED_5' 		: [str.encode("SI") + str.encode('5'),  str.encode("ok")],
    'INWARD_SPEED_6' 		: [str.encode("SI") + str.encode('6'),  str.encode("ok")],
    'OUTWARD_SPEED_1'		: [str.encode("SO") + str.encode('1'),  str.encode("ok")],
    'OUTWARD_SPEED_2'		: [str.encode("SO") + str.encode('2'),  str.encode("ok")],
    'OUTWARD_SPEED_3'		: [str.encode("SO") + str.encode('3'),  str.encode("ok")],
    'OUTWARD_SPEED_4'		: [str.encode("SO") + str.encode('4'),  str.encode("ok")],
    'OUTWARD_SPEED_5'		: [str.encode("SO") + str.encode('5'),  str.encode("ok")],
    'OUTWARD_SPEED_6'		: [str.encode("SO") + str.encode('6'),  str.encode("ok")],
    'EJECT_AND_HOME'    	: [str.encode("RE") + str.encode('30'),	str.encode("ok")],
    'RUN_TIP_EJECT_CYCLE'	: [str.encode("RE"),  					str.encode("ok")],
    'RUN_BLOWOUT'			: [str.encode("RB"),  					str.encode("ok")],
}

DISPLAY_COMMANDS = {
    'DISPLAY_VERSION'		: [str.encode("DV"),  					str.encode("dv")],
    'DISPLAY_MODEL'			: [str.encode("DV"),  					str.encode("dm")],
    'DISPLAY_CYCLES'		: [str.encode("DX"),  					str.encode("dx")],
    'DISPLAY_IN_SPEED'		: [str.encode("DI"),  					str.encode("di")],
    'DISPLAY_OUT_SPEED'		: [str.encode("DO"),  					str.encode("do")],
    'DISPLAY_RESOLUTION'	: [str.encode("DR"),  					str.encode("dr")],
    'DISPLAY_STATUS'		: [str.encode("DS"),  					str.encode("ds")],
    'DISPLAY_ERRORS'		: [str.encode("DE"),  					str.encode("de")],
    'DISPLAY_POSITION'		: [str.encode("DP"),  					str.encode("dp")],
    'DISPLAY_LIQUID_LEVEL'	: [str.encode("DN"),  					str.encode("dn")],
}

POSITIONAL_COMMANDS = {
    'RUN_TO_POSITION'		: [str.encode("RP"),  str.encode("ok")], #position: nnn, without leading zeros
    'RUN_INWARDS'			: [str.encode("RI"),  str.encode("ok")], #position: nnn, without leading zeros
    'RUN_OUTWARDS'			: [str.encode("RO"),  str.encode("ok")], #position: nnn, without leading zeros
    'TIP_EJECT_AND_MOVE'	: [str.encode("RE"),  str.encode("ok")], #position: nnn, without leading zeros
    'BLOWOUT_AND_MOVE'		: [str.encode("RB"),  str.encode("ok")], #position: nnn, without leading zeros
}

class Pipette():
    #constructor
    def __init__(self, port):
        """Creates the serial port object and sets the parameters for the pipette controller."""
        self.port = serial.Serial()
        self.port.port = port
        self.port.baudrate = 9600
        self.port.parity=serial.PARITY_NONE
        self.port.stopbits=serial.STOPBITS_ONE
        self.port.bytesize=serial.EIGHTBITS
        self.port.timeout = 1
        self.multiplier=1

    def parseError(self, answer):
        """Parses the error code and prints the corresponding error message.
        Args:
            answer (str): The answer received from the pipette controller."""
        if ERROR_CODES["err_codes"][0] in answer:
            #logging.error("Command has not been understood by the module")
            print("Command has not been understood by the module")
        elif ERROR_CODES["err_codes"][1] in answer:
            print("Command has been understood but would result in out-of-bounds state")
        elif ERROR_CODES["err_codes"][2] in answer:
            print("LRC is configured to be used and the checksum does not matc")
        elif ERROR_CODES["err_codes"][3] in answer:
            print("The drive is on and the command or query cannot be answered.")
        else:
            print("Error code unrecognized!")

    def waitAck(self, ans):
        """Waits for the acknowledge from the pipette controller.
        Args:
            ans (str): The acknowledge message to wait for.
        Returns:
            bool: True if the acknowledge has been received, False otherwise.
            int: The length of the received message.
        """
        char = self.port.read(1)
        answer = str(char)
        while(char):
            char = self.port.read(1)
            answer += str(char)
        logging.debug(answer)
        if ans in answer:
            logging.debug("Acknowledge received")
            return (True, len(answer))
        else:
            logging.debug("nack received")
            self.parseError(answer)
            return (False, len(answer))

    def readFeedback(self):
        """Reads the feedback from the pipette controller.
        Returns:
            str: The feedback message received from the pipette controller.
        """
        read = self.port.read_until(b'\r')
        return read
    
    def check_connection(self):
        """Checks if the connection to the pipette controller is established.
        Returns:
            bool: True if the connection is established, False otherwise.
        """
        return self.port.isOpen()

    def sendCmd(self, cmd, pos = 1):
        """Sends a command to the pipette controller.
        Args:
            cmd (str): The command to be sent to the pipette controller.
            pos (int, optional): The position to be sent to the pipette controller. Defaults to 1.
        Returns:
            bool: True if the command has been executed successfully, False otherwise.
            int: The position of the pipette controller.
        """
        if cmd in REGULAR_COMMANDS.keys():
            msg = PRE + str.encode(ADR) +  REGULAR_COMMANDS[cmd][0] + POST
            self.port.write(msg)
            #time.sleep(0.05)
            res = self.port.read_until(b'\r')
            if b'er' in res:
                self.parseError(res)
            elif REGULAR_COMMANDS[cmd][1] in res:
                return (True, REGULAR_COMMANDS[cmd][0])
        elif cmd in DISPLAY_COMMANDS.keys():
            msg = PRE + str.encode(ADR) +  DISPLAY_COMMANDS[cmd][0] + POST
            self.port.write(msg)
            #time.sleep(0.05)
            res = self.port.read_until(b'\r')
            while not DISPLAY_COMMANDS[cmd][1] in res:
                res = self.port.read_until(b'\r')
            return int(res[4:-2])
        elif cmd in POSITIONAL_COMMANDS.keys():
            msg = PRE + str.encode(ADR) +  POSITIONAL_COMMANDS[cmd][0] + str.encode(str(pos)) + POST
            self.port.write(msg)
            #time.sleep(0.05)
            res = self.port.read_until(b'\r')
            if b'er' in res:
                self.parseError(res)
            elif POSITIONAL_COMMANDS[cmd][1] in res:
                return (True, POSITIONAL_COMMANDS[cmd][0])

    def tellPosition(self):
        """Tells the position of the pipette controller.
        Returns:
            int: The position of the pipette controller.
        """
        return self.sendCmd("DISPLAY_POSITION")
        # res = self.readFeedback()
        # while not b'dp' in res:
        #     res = self.readFeedback()
        # return int(res[4:-2])
        
    def tellLevel(self):
        """Tells the liquid level of the pipette controller.
        Returns:
            int: The liquid level of the pipette controller.
        """
        return self.sendCmd("DISPLAY_LIQUID_LEVEL")
        # res = self.readFeedback()
        # while not b'dn' in res:
        #     res = self.readFeedback()
        # return int(res[4:-2])

    def initialize(self):
        """Initializes the pipette controller.
        Returns:
            bool: True if the initialization has been successful, False otherwise.
        """
        con_res = self.check_connection()
        if con_res == True:
            pass
        else:
            self.port.open()
        time.sleep(0.2)
        home_res = self.sendCmd("RESET")
        #print(self.readFeedback())
        time.sleep(5)
        speed1_res = self.sendCmd("INWARD_SPEED_3")
        # print(self.readFeedback())
        time.sleep(1)
        speed2_res = self.sendCmd("OUTWARD_SPEED_3")
        # print(self.readFeedback())
        return all([con_res, home_res[0], speed1_res[0], speed2_res[0]])

    def aspirate(self, volume):
        """Aspirates the given volume.
        Args:
            volume (int): The volume to be aspirated.
        Returns:
            bool: True if the aspiration has been successful, False otherwise.
        """
        #print(round(volume/20))
        return self.sendCmd("RUN_INWARDS", round(volume/10))

    def dispense(self, volume):
        """Dispenses the given volume.
        Args:
            volume (int): The volume to be dispensed.
        Returns:
            bool: True if the dispensing has been successful, False otherwise.
        """
        return self.sendCmd("RUN_OUTWARDS", round(volume/10))

    def clear_and_reset(self):
        """Clears and resets the pipette controller.
        Returns:
            bool: True if the clearing and resetting has been successful, False otherwise.
        """
        return self.sendCmd("BLOWOUT_AND_MOVE", 30)

    def reset(self):
        """Resets the pipette controller.
        Returns:
            bool: True if the resetting has been successful, False otherwise.
        """
        return self.sendCmd("RESET")

    def blowout(self):
        """Blows out the pipette.
        Returns:
            bool: True if the blowout has been successful, False otherwise.
        """
        return self.sendCmd('RUN_BLOWOUT')

    def eject(self):
        """Ejects the tip.
        Returns:
            bool: True if the tip has been ejected successfully, False otherwise.
        """
        return self.sendCmd("RUN_TIP_EJECT_CYCLE")

    def eject_and_home(self):
        """Ejects the tip and homes the pipette.
        Returns:
            bool: True if the tip has been ejected and the pipette has been homed successfully, False otherwise.
        """
        return self.sendCmd("EJECT_AND_HOME")

    def disconnect_pipette(self):
        """Disconnects the pipette controller.
        Returns:
            str: The message indicating that the pipette controller has been disconnected.
        """
        self.port.close()
        return 'PipetteController disconnected!'
