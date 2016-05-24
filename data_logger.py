import sys
from datetime import datetime
import random
import time
from threading import *

portA, portB = None, None
data = {'dataA':{}, 'dataB': {}}
DELAY = 10
lock = Lock()
time_now = None
flag = False                     # True -> Use serial , False -> Use random

def config():
    global portA, portB
    if len(sys.argv) == 2:
        port_a = sys.argv[1]
        port_b = sys.argv[2]
    try:
        from serial import Serial
        portA  = Serial(port_a)
        portB  = Serial(port_b)        
    except Exception as e:
        print 'Module not found'
    
def readA(name, delay):
    print 'read started A'
    global data, lock, time_now, flag
    import thread
    thread.start_new_thread(readB, ('readB', DELAY,))
    while True:
        time_now = time.mktime(datetime.now().timetuple()) * 1000        
        lock.acquire()
        if flag:
             data['dataA'][time_now] = portA.readline()
        else:
             data['dataA'][time_now] = random.randint(1, 10)            
        lock.release()

def readB(name, delay):
    print 'read started B'
    global data, lock, time_now, flag
    while True:
        lock.acquire()
        if flag:
             data['dataB'][time_now] = portA.readline()
        else:
             data['dataB'][time_now] = random.randint(1, 10)
        lock.release()

def write_tofile():
    global data, lock
    lock.acquire()
    import uuid
    file_name = '%s_out.csv' % str(uuid.uuid4())
    file = open(file_name, 'wb')
    keys = sorted(data['dataA'], key = data['dataA'].get)
    for k in keys:
        if k in data['dataA']:
            dataA = data['dataA'][k]
        else:
            dataA = None
        if k in data['dataB']:
            dataB = data['dataB'][k]
        else:
            dataB = None
        file.write("%s,%s,%s\n" % (k, dataA, dataB))
    file.close()
    lock.release()
    return file_name

# Example Usage -> python pyapp.py COM1 COM2
if __name__ == '__main__':
    config()
    import thread
    thread.start_new_thread(readA, ('readA', DELAY,))
    while True:
        try:
            user_input = input()
        except KeyboardInterrupt as e:
            if flag:
                portA.close()
                portB.cloe()
            file = write_tofile()
            # global data
            # print 'Written %d bytes to file %s' % (sys.getsizeof(data), file)
            sys.exit()
