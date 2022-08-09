import time


def formated_time(t):
    return time.strftime("%H:%M:%S", time.localtime(t))
