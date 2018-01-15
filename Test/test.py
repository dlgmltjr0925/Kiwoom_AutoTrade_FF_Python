import threading, time

count = 0

def start_timer():
    timer = threading.Timer(1, begin_timer)
    timer.start()
    for i in range(15):
        time.sleep(0.1)
        print(i)

def begin_timer():
    print('timer')

start_timer()
