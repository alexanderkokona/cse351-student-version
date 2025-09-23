from cse351 import *
import threading
import time

def print_cool_stuff(mutex):
    mutex.aquire()
    print('cool stuff')
    mutex.release()

t = threading.Thread(target=print_cool_stuff, args=(mutex,))
t.start()
mutex.aquire()

print('hello world')
