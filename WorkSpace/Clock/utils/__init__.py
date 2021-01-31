
import _thread
import threading
import time

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