
import _thread
import threading
import time

import logging

def runAsync(work, delay = 0):
    def _workFunc(w,d):
        if (d > 0):
            time.sleep(d)
        w()
    _thread.start_new_thread(_workFunc, (work, delay))
    pass

def dumpThreads(label):
    print('dump threads --->> in', label,)
    for t in threading.enumerate():
        print('\tthread', t, t.name, threading.current_thread() == t)
    pass


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"

COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': CYAN,
    'ERROR': MAGENTA,
    'CRITICAL': RED
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        logging.Formatter.__init__(self, fmt=fmt, datefmt=datefmt, style=style)

    def format(self, record):
        levelname = record.levelname
        message = str(record.msg)
        funcName = record.funcName
        if levelname in COLORS:
            # print('format log')
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            message_color = COLOR_SEQ % (30 + COLORS[levelname]) + message + RESET_SEQ
            funcName_color = COLOR_SEQ % (30 + COLORS[levelname]) + funcName + RESET_SEQ
            record.levelname = levelname_color
            record.msg = message_color
            record.funcName = funcName_color
        return logging.Formatter.format(self, record)

def clampPercent(input_value, min_value, max_value):
    if input_value < min_value:
        return 0
    if input_value > max_value:
        return 100
    value_range = max_value - min_value
    return (input_value - min_value) / value_range * 100
