
import _thread

def runAsync(work):
    _thread.start_new_thread(work, ())
    pass