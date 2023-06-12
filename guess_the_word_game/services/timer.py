import time


def start_timer():
    return time.time()


def elapsed_time(start_time):
    return time.time() - float(start_time)
