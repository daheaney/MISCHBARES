"""motor driver"""
import time

import json
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket
import uvicorn

from mischbares.config.main_config import config
from mischbares.driver.motor_driver import *
from mischbares.logger import logger
from mischbares.utils import utils

log = logger.get_logger("motor_server")
SERVERKEY= "motorDriver"


app = FastAPI(title="Motor", description="MotorDriver API", version="1.0.0")


class ReturnClass(BaseModel):
    """
    define a return class for returning the result with pydantic
    """
    parameters: dict = None
    data: dict = None

