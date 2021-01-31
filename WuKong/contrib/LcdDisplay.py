# -*- coding: utf-8-*-
import socket
import requests
from robot.sdk import UIClock
from robot import config, logging
from robot.sdk.AbstractPlugin import AbstractPlugin
import os

logger = logging.getLogger(__name__)

class Plugin(AbstractPlugin):

    def handle(self, text, parsed):
        #os.system("sudo ttyecho -n /dev/tty1 ehco "+ text)
        print('LcdDisplay text =', text, '  parsed =', parsed)
        try:
            #payload = {'robot_msg': text}
            UIClock.think(text)
        except:
            print('LcdDisplay request failed')
        return True


    def isValid(self, text, parsed):
        return True #'lcd:' in text
