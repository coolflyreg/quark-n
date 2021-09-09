#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import time
import re
import json
import socket
from utils import clampPercent

def cputempf():
    f = open("/sys/class/thermal/thermal_zone0/temp")
    CPUTemp = f.read()
    f.close()
    StringToOutput = "CPU {0} C".format(round(int(CPUTemp) /1000.0, 2))
    return StringToOutput, int(CPUTemp) /1000.0

# Return % of CPU used by user as a character string
# def getCPUuse():
#     return (str(os.popen("top -b -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip()))

def readCpuInfo(): 
    f = open ( '/proc/stat' )
    lines = f.readlines()
    f.close()
    for line in lines:
        line = line.lstrip()
        counters = line.split()
        if len (counters) < 5 :
            continue
        if counters[ 0 ].startswith( 'cpu' ):
            break
    total = 0
    for i in range ( 1 , len (counters)):
        total = total + int (counters[i])
    idle = int (counters[ 4 ])
    return { 'total' :total, 'idle' :idle}
    
def calcCpuUsage(counters1, counters2):
     idle = counters2[ 'idle' ] - counters1[ 'idle' ]
     total = counters2[ 'total' ] - counters1[ 'total' ]
     return 100 - (idle * 100 / total)

def getCpuUsage():
    counters1 = readCpuInfo()
    time.sleep( 0.1 )
    counters2 = readCpuInfo()
    return (round(calcCpuUsage(counters1, counters2), 1))


def get_host_ip(): 
    s = None
    ip = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except OSError as e:
        #print('network can\'t be reached!')
        ip = 'No Network'
    finally:
        if s is not None:
            s.close()
    return ip


def get_mem_info():
    mem_info = {}
    mem_info['total'] = 0
    mem_info['free'] = 0
    mem_info['buffers'] = 0
    mem_info['cached'] = 0
    mem_info['cached_percent'] = 0
    mem_info['used'] = 0
    mem_info['percent'] = 0
    mem_info['real'] = {}
    mem_info['real']['used'] = 0
    mem_info['real']['free'] = 0
    mem_info['real']['percent'] = 0
    mem_info['swap'] = {}
    mem_info['swap']['total'] = 0
    mem_info['swap']['free'] = 0
    mem_info['swap']['used'] = 0
    mem_info['swap']['percent'] = 0

    mem_info_file = open('/proc/meminfo')
    if mem_info_file is not None:
        mem_info_content = mem_info_file.read()
        mem_info_content = mem_info_content.replace('\n', ' ')
        buf = re.findall(
            r'MemTotal\s{0,}\:+\s{0,}([\d\.]+).+?MemFree\s{0,}\:+\s{0,}([\d\.]+).+?Cached\s{0,}\:+\s{0,}([\d\.]+).+?SwapTotal\s{0,}\:+\s{0,}([\d\.]+).+?SwapFree\s{0,}\:+\s{0,}([\d\.]+)',
            mem_info_content)
        buffers = re.findall(r'Buffers\s{0,}\:+\s{0,}([\d\.]+)', mem_info_content)

        mem_info['total'] = round(int(buf[0][0])/1024, 2)
        mem_info['free'] = round(int(buf[0][1])/1024, 2)
        mem_info['buffers'] = round(int(buffers[0])/1024, 2)
        mem_info['cached'] = round(int(buf[0][2]) / 1024, 2)
        mem_info['cached_percent'] = (round(mem_info['cached'] / mem_info['total'] * 100, 2) if (float(mem_info['cached']) != 0) else 0)
        mem_info['used'] = mem_info['total'] - mem_info['free']
        mem_info['percent'] = (round(mem_info['used'] / mem_info['total'] * 100, 2) if (float(mem_info['total']) != 0) else 0)
        mem_info['real']['used'] = mem_info['total'] - mem_info['free'] - mem_info['cached'] - mem_info['buffers']
        mem_info['real']['free'] = round(mem_info['total'] - mem_info['real']['used'], 2);
        mem_info['real']['percent'] = (round(mem_info['real']['used'] / mem_info['total'] * 100, 2) if (float(mem_info['total']) != 0) else 0)
        mem_info['swap']['total'] = round(int(buf[0][3]) / 1024, 2)
        mem_info['swap']['free'] = round(int(buf[0][4]) / 1024, 2)
        mem_info['swap']['used'] = round(mem_info['swap']['total'] - mem_info['swap']['free'], 2)
        mem_info['swap']['percent'] = (round(mem_info['swap']['used'] / mem_info['swap']['total'] * 100, 2) if (float(mem_info['swap']['total']) != 0) else 0)

    return mem_info

def get_disk_info():
    disk_info = {
        'total': '0',
        'free': '0',
        'used': '0',
        'percent': '0'
    }

    p = os.popen("df -h /")
    # i = 0
    # while 1:
    #     i = i +1
    #     line = p.readline()
    #     if i==2:
    #         disk_info_lines = (line.split()[1:5])

    #         disk_info['total'] = disk_info_lines[0]
    #         disk_info['used'] = disk_info_lines[1]
    #         disk_info['free'] = disk_info_lines[2]
    #         disk_info['percent'] = disk_info_lines[3]

    #         return disk_info
    line = p.readline()
    line = p.readline()
    disk_info_lines = (line.split()[1:5])

    disk_info['total'] = disk_info_lines[0]
    disk_info['used'] = disk_info_lines[1]
    disk_info['free'] = disk_info_lines[2]
    disk_info['percent'] = disk_info_lines[3]

    def parseToByteCount(str_val):
        unit = str_val[-1:]
        val = float(str_val[:-1])
        if (unit == 'G'):
            val = val * 1024 * 1024 * 1024
        if (unit == 'M'):
            val = val * 1024 * 1024
        if (unit == 'K'):
            val = val * 1024
        return val

    total = parseToByteCount(disk_info['total'])
    used = parseToByteCount(disk_info['used'])
    free = parseToByteCount(disk_info['free'])

    disk_info['used_percent'] = clampPercent(used, 0, total)
    disk_info['free_percent'] = clampPercent(free, 0, total)

    return disk_info


def get_battery_info():
    battery_filepath = '/var/battery/info.json'
    if os.path.exists(battery_filepath):
        try:
            f = open(battery_filepath, 'r')
            content = f.read()
            f.close()
            jsonObj = json.loads(content)
            vbat = float(jsonObj['vbat'])
            vout = float(jsonObj['vout'])
            chgr_current = float(jsonObj['chgr_current'])
            out_current = float(jsonObj['out_current'])
            return {
                'percent': clampPercent(vbat, 3.0, (3.72 if chgr_current == 0 else 4.2)),
                'in_charge': (chgr_current > 0)
            }
        except:
            # print (e)
            return None
    return None