import time


def start_timer():
    return time.time()


def elapsed_time(start_time):
    return time.time() - start_time
