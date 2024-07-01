"""motor driver"""
import time

import json
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket
import uvicorn

from mischbares.config.main_config import config
from mischbares.driver.motor_driver import Motor
from mischbares.logger import logger

log = logger.get_logger("motor_server")
SERVERKEY= "motorDriver"


motor = None

app = FastAPI(title="Motor server",
    description="This is a motor driver server for Nema stepper motors.",
    version="1.0.0")


class return_class(BaseModel):
    parameters: dict = None
    data: dict = None

@app.get("/health")
def health_check():
    """ health check to see if the server is up and running
    Returns:
        dict: status
    """
    return {"status": "healthy"}

@app.get("/motorDriver/check_connection")
def check_connection():
    """Checks if the motor is connected
    Returns:
        retc (return_class): return class with the parameters and the data
    """
    motor.check_connection()
    retc = return_class(parameters={},data={})
    return retc

@app.get("/motorDriver/set_speed")
def set_speed(speed: int):
    """Sets the speed of the motor
    Args:
            speed (int): The speed to set the motor to. Must be between 0 and 1000.
    Returns:
        retc (return_class): return class with the parameters and the data
    """
    motor.set_speed(speed)
    retc = return_class(parameters={'speed': speed,
                            'units':{'speed':'steps/sec'}},
                            data={})
    return retc

@app.get("/motorDriver/stop")
def stop():
    """Stops the motor
    Returns:
        retc (return_class): return class with the parameters and the data
    """
    motor.stop()
    retc = return_class(parameters={},data={})
    return retc

@app.get("/motorDriver/set_acceleration")
def set_acceleration(acceleration: int):
    """Sets the acceleration of the motor
    Args:
            acceleration (int): The acceleration to set the motor to. Must be between 0 and 1000.
    Returns:
        retc (return_class): return class with the parameters and the data
    """
    motor.set_acceleration(acceleration)
    retc = return_class(parameters={'acceleration': acceleration,
                            'units':{'acceleration':'steps/sec^2'}},
                            data={})
    return retc

@app.get("/motorDriver/move")
def move(steps: int):
    """Moves the motor
    Args:
            steps (int): The number of steps to move the motor.
    Returns:
        retc (return_class): return class with the parameters and the data
    """
    motor.move(steps)
    retc = return_class(parameters={'steps': steps,
                            'units':{'steps':'steps'}},
                            data={})
    return retc

@app.get("/motorDriver/wait_for_motor")
def wait_for_motor():
    """Wait for acknowledgment from the motor that task is finished"""
    motor.wait_for_motor()
    retc = return_class(parameters={},data={})
    return retc




