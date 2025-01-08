import time


def get_formatted_time() -> str:
    t = time.time()
    return time.strftime('%H:%M:%S', time.localtime(t)) + f'.{int((t % 1) * 1000):03d}'
