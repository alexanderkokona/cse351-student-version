"""
Course: CSE 351
Team  :
File  : Week 9 team.py
Author:  Luc Comeau (student implementation by your team)
"""

from cse351 import *
import time
import random
import multiprocessing as mp

# number of cleaning staff and hotel guests
CLEANING_STAFF = 2
HOTEL_GUESTS = 5

# Run program for this number of seconds
TIME = 60

STARTING_PARTY_MESSAGE =  'Turning on the lights for the party vvvvvvvvvvvvvv'
STOPPING_PARTY_MESSAGE  = 'Turning off the lights  ^^^^^^^^^^^^^^^^^^^^^^^^^^'

STARTING_CLEANING_MESSAGE =  'Starting to clean the room >>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
STOPPING_CLEANING_MESSAGE  = 'Finish cleaning the room <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'


def cleaner_waiting():
    time.sleep(random.uniform(0, 2))

def cleaner_cleaning(id):
    print(f'Cleaner: {id}')
    time.sleep(random.uniform(0, 2))

def guest_waiting():
    time.sleep(random.uniform(0, 2))

def guest_partying(id, count):
    print(f'Guest: {id}, count = {count}')
    time.sleep(random.uniform(0, 1))


def cleaner(id, start_time, room_lock, guest_count, guest_count_lock,
            cleaned_count):
    while time.time() - start_time < TIME:
        cleaner_waiting()

        # cleaners need exclusive access
        room_lock.acquire()

        print(STARTING_CLEANING_MESSAGE)
        cleaner_cleaning(id)
        print(STOPPING_CLEANING_MESSAGE)

        with cleaned_count.get_lock():
            cleaned_count.value += 1

        room_lock.release()


def guest(id, start_time, room_lock, guest_count, guest_count_lock,
          party_count):
    while time.time() - start_time < TIME:
        guest_waiting()

        # entering guest
        with guest_count_lock:
            if guest_count.value == 0:
                # first guest must lock the room for cleaners
                room_lock.acquire()
                print(STARTING_PARTY_MESSAGE)
                with party_count.get_lock():
                    party_count.value += 1

            guest_count.value += 1
            current_count = guest_count.value

        # guest is partying
        guest_partying(id, current_count)

        # leaving guest
        with guest_count_lock:
            guest_count.value -= 1
            if guest_count.value == 0:
                # last guest leaves → unlock cleaners and lights off
                print(STOPPING_PARTY_MESSAGE)
                room_lock.release()


def main():
    start_time = time.time()

    # shared state
    room_lock = mp.Lock()
    guest_count_lock = mp.Lock()

    guest_count = mp.Value('i', 0)
    party_count = mp.Value('i', 0)
    cleaned_count = mp.Value('i', 0)

    processes = []

    # cleaners
    for i in range(1, CLEANING_STAFF + 1):
        p = mp.Process(target=cleaner,
                       args=(i, start_time,
                             room_lock, guest_count, guest_count_lock,
                             cleaned_count))
        processes.append(p)
        p.start()

    # guests
    for i in range(1, HOTEL_GUESTS + 1):
        p = mp.Process(target=guest,
                       args=(i, start_time,
                             room_lock, guest_count, guest_count_lock,
                             party_count))
        processes.append(p)
        p.start()

    # wait for all to finish
    for p in processes:
        p.join()

    print(f'Room was cleaned {cleaned_count.value} times, there were {party_count.value} parties')


if __name__ == '__main__':
    main()
