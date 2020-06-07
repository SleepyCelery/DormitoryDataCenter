import multiprocessing
import time


def print_time():
    print('2')


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=4)
    pool.apply_async(print_time)
    time.sleep(5)

