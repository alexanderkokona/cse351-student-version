"""
Course: CSE 351 
Week: 07 Team
File:   team.py
Author: <Your Name>

Purpose: Solve the Dining philosophers problem to practice skills you have learned so far in this course.

Problem Statement:

Five silent philosophers sit at a round table with bowls of spaghetti. Forks
are placed between each pair of adjacent philosophers.

Each philosopher must alternately think and eat. However, a philosopher can
only eat spaghetti when they have both left and right forks. Each fork can be
held by only one philosopher and so a philosopher can use the fork only if it
is not being used by another philosopher. After an individual philosopher
finishes eating, they need to put down both forks so that the forks become
available to others. A philosopher can only take the fork on their right or
the one on their left as they become available and they cannot start eating
before getting both forks.  When a philosopher is finished eating, they think 
for a little while.

Eating is not limited by the remaining amounts of spaghetti or stomach space;
an infinite supply and an infinite demand are assumed.

The problem is how to design a discipline of behavior (a concurrent algorithm)
such that no philosopher will starve
"""

import time
import random
import threading

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
PHILOSOPHERS = 5
MAX_MEALS_EATEN = PHILOSOPHERS * 5  # total meals before stopping
DELAY = 1.0  # optional speed control

# Shared counters (need thread-safe access)
meal_count = 0
meals = [0] * PHILOSOPHERS
meal_lock = threading.Lock()  # protects shared meal counters


# --------------------------------------------------------------------------
# Philosopher Class
# --------------------------------------------------------------------------
class Philosopher(threading.Thread):
    def __init__(self, pid, left_fork, right_fork):
        threading.Thread.__init__(self)
        self.pid = pid
        self.left_fork = left_fork
        self.right_fork = right_fork

    def run(self):
        global meal_count

        while True:
            # Check if we’re done (protected by meal_lock)
            with meal_lock:
                if meal_count >= MAX_MEALS_EATEN:
                    break

            # Try to acquire left fork
            self.left_fork.acquire()
            # Try to acquire right fork (non-blocking)
            if not self.right_fork.acquire(blocking=False):
                # Couldn’t get both forks – put left back down and swap order
                self.left_fork.release()
                self.left_fork, self.right_fork = self.right_fork, self.left_fork
                continue

            # Eat
            self.eat()

            # Update counters
            with meal_lock:
                meal_count += 1
                meals[self.pid] += 1

            # Release both forks
            self.left_fork.release()
            self.right_fork.release()

            # Think
            self.think()

    def eat(self):
        print(f"Philosopher {self.pid} starts eating.")
        time.sleep(random.uniform(1, 3) / DELAY)
        print(f"Philosopher {self.pid} finishes eating.")

    def think(self):
        print(f"Philosopher {self.pid} starts thinking.")
        time.sleep(random.uniform(1, 3) / DELAY)
        print(f"Philosopher {self.pid} stops thinking.")


# --------------------------------------------------------------------------
# Main Program
# --------------------------------------------------------------------------
def main():
    global meal_count
    meal_count = 0

    # Create forks (locks)
    forks = [threading.Lock() for _ in range(PHILOSOPHERS)]

    # Create philosophers (each needs two adjacent forks)
    philosophers = [
        Philosopher(i, forks[i % PHILOSOPHERS], forks[(i + 1) % PHILOSOPHERS])
        for i in range(PHILOSOPHERS)
    ]

    # Start all threads
    for p in philosophers:
        p.start()

    # Wait for all threads to finish
    for p in philosophers:
        p.join()

    # Display results
    print("\n--- Simulation Complete ---")
    print(f"Total meals eaten: {meal_count}")
    for i in range(PHILOSOPHERS):
        print(f"Philosopher {i} ate {meals[i]} times.")


if __name__ == '__main__':
    main()
