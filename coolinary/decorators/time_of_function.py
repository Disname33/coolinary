import time


def time_of_function(function):
    def wrapped(*args):
        start_time = time.time()
        res = function(*args)
        timer = time.time() - start_time
        timer_c = int(timer)
        timer_mc = int(timer * 1000) % 1000
        timer_nc = int(timer * 1000000) % 1000
        print(f'Затраченное время: {timer_c} секунд, {timer_mc} м.с, {timer_nc} н.с.')
        return res

    return wrapped
