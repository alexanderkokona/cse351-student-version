from datetime import datetime, timedelta
import threading
import random

from cse351 import *

prime_count = 0
numbers_processed = 0
lock = threading.Lock()   

def is_prime(n):
    """
        Primality test using 6k+-1 optimization.
        From: https://en.wikipedia.org/wiki/Primality_test
    """
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def worker(start, end):
    """Thread worker: process a slice of the range."""
    global prime_count, numbers_processed
    local_primes = 0
    local_processed = 0

    for i in range(start, end):
        local_processed += 1
        if is_prime(i):
            local_primes += 1
            print(i, end=', ', flush=True)

    with lock:
        prime_count += local_primes
        numbers_processed += local_processed


def main():
    global prime_count, numbers_processed

    log = Log(show_terminal=True)
    log.start_timer()

    start = 10_000_000_000
    range_count = 100_007   

    num_threads = 10
    chunk_size = range_count // num_threads
    threads = []

    for t in range(num_threads):
        chunk_start = start + t * chunk_size
        if t == num_threads - 1:
            chunk_end = start + range_count
        else:
            chunk_end = chunk_start + chunk_size
        thread = threading.Thread(target=worker, args=(chunk_start, chunk_end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(flush=True)
    log.write(f'Numbers processed = {numbers_processed}')
    log.write(f'Primes found      = {prime_count}')
    log.stop_timer('Total time')


if __name__ == '__main__':
    main()
