#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import fire
from ruamel.yaml import YAML
import logging
import logging.config
# import pygame
import signal
from system.config import Config

# print('fontfile path: ', os.getcwd(), sys.path)
os.chdir(sys.path[0])
if bool(Config().get('debug.remote')):
    import pydevd
    pydevd.settrace('192.168.1.88', port=31000, stdoutToServer=True, stderrToServer=True)

# logging.config.fileConfig('logging.conf')
with open('logging.yaml', "r") as f:
    yaml = YAML()
    config = yaml.load(f)
    logging.config.dictConfig(config)
    log_colors_config = {
        'DEBUG': 'white',  # cyan white
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }

logger = logging.getLogger('main')

class Main(object):

    def run(self):
        import App
        App.main()
        pass

    def restart(self):
        logger.critical('程序重启...')
        try:
            self.shutdown()
        except:
            pass
        python = sys.executable
        os.execl(python, python, sys.argv[0])
        pass

    def shutdown(self):
        pidFile = Config().get('monitor.pid-file', '/run/ui_clock.pid')
        if os.path.exists(pidFile):
            print('pid file is {}'.format(pidFile))
            with open(pidFile, 'r') as f:
                pid = int(f.readline().replace('\n', '').replace('\r', ''))
                retCode = os.system('kill -s TERM {}'.format(pid))
                if retCode == 0:
                    print('{} is killed'.format(pid))
                else:
                    print('killing pid {} by return code {}'.format(pid, retCode))
        else:
            print('Can\'t find pid file.')
        pass

    def help(self):
        print('print help')
        pass

    pass

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main = Main()
        main.run()
    elif '-h' in (sys.argv):
        main = Main()
        main.help()
    else:
        fire.Fire(Main)