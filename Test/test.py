import threading as tr, time

count = 0

def start_timer():
    for i in range(5):
        print('{}[before] : {}'.format(i, tr.active_count()))
        tr.Timer(1, begin_timer).start()
        print('{}[after] : {}'.format(i, tr.active_count()))
        print(type(tr.active_count()))
        time.sleep(0.1)
        print(i)

def begin_timer():
    print('timer')

start_timer()
