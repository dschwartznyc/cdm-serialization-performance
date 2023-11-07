import timeit
import inspect
import time

def sleep_it ():
    time.sleep(30)
    
timings   = timeit.repeat(sleep_it, number=1, repeat=1)
print(timings)
