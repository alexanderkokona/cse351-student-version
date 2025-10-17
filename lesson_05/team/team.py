"""
Course: CSE 351
Lesson: L05 Team Activity
File:   team.py
Author: Alexander Kokona
Purpose: Find prime numbers using multiprocessing.Pool

Instructions:

- Don't include any other Python packages or modules
- Review and follow the team activity instructions (team.md)
"""

from datetime import datetime
import multiprocessing as mp
from matplotlib.pylab import plt  # load plot library

# Include CSE 351 common Python files
from cse351 import *


def is_prime(n):
    """Return True if n is a prime number."""
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


def process_number(number):
    """Return the number if it is prime, otherwise None."""
    if is_prime(number):
        return number
    return None


def main():
    log = Log(show_terminal=True)
    log.start_timer()

    xaxis_cpus = []
    yaxis_times = []

    start = 10_000_000_000
    range_count = 100_000
    numbers = list(range(start, start + range_count))

    print(f"System has {mp.cpu_count()} CPU cores available.\n")

    for pool_size in range(1, mp.cpu_count() + 1):
        print(f"Pool of {pool_size:2} CPU cores", end='')

        xaxis_cpus.append(pool_size)

        start_time = datetime.now()

        with mp.Pool(pool_size) as pool:
            results = pool.map(process_number, numbers)

        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        yaxis_times.append(elapsed_time)

        # Count primes by ignoring None values
        prime_count = sum(1 for r in results if r is not None)

        print(f" took {elapsed_time:.2f} seconds | Primes found: {prime_count}")

    # Plot the results
    plt.plot(xaxis_cpus, yaxis_times, marker='o', label='Processing Time')
    plt.title('Time vs CPU Cores')
    plt.xlabel('CPU Cores')
    plt.ylabel('Seconds')
    plt.legend(loc='best')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    log.stop_timer("Program complete")


if __name__ == '__main__':
    main()
