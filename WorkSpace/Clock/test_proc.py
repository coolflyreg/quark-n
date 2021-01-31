# -*- coding: UTF-8 -*-
import os
import sys
import subprocess
import signal
from system.config import Config
from multiprocessing import Process


def main():
    cmd = ['su', 'pi', '-c', '"/usr/bin/sudo python /home/pi/WorkSpace/WuKong/wukong-robot/wukong.py"']

    wukongRoot = Config().get('robot.wukong.root')
    print(wukongRoot)
    cmd = ' '.join(cmd)
    print(cmd)
    proc = subprocess.Popen(cmd, cwd=wukongRoot, shell=True)#, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # proc = subprocess.run(' '.join(cmd), cwd=wukongRoot, shell=True, capture_output=True)
    print(proc)
    if proc.poll() is not None:
        print('WuKong Process is exited with code:', proc.poll())
        proc = None


# proc = WuKongProcess(name='WuKong') 
# proc.start()
# proc.join()

if __name__ == '__main__':
    main()