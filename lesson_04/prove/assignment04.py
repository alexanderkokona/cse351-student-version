"""
Course    : CSE 351
Assignment: 04
Student   : Alexander Kokona

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}

where:

name: name of the city
recno: record number starting from 0

"""

import time
from common import *

from cse351 import *

import threading
import queue

THREADS = 200
WORKERS = 100
RECORDS_TO_RETRIEVE = 5000  # Don't change


# ---------------------------------------------------------------------------
def retrieve_weather_data(cmd_q, data_q):
    """
    Thread function: consumes commands from cmd_q (tuples (city, recno)),
    calls the server for the specific record, then places (city, date, temp)
    onto data_q for worker threads to process.

    Uses sentinel None to stop: when a None is received from cmd_q, the thread
    marks the task done and exits.
    """
    while True:
        item = cmd_q.get()
        try:
            if item is None:
                # propagate sentinel handling
                cmd_q.task_done()
                break

            city, recno = item
            # build URL and request data using provided helper
            url = f'{TOP_API_URL}/record/{city}/{recno}'
            try:
                record = get_data_from_server(url)
            except Exception:
                # On transient server error, we can retry a small number of times
                # but to keep simple and robust for the assignment, try once more
                try:
                    record = get_data_from_server(url)
                except Exception as e:
                    # If still failing, skip this record (but mark task done)
                    cmd_q.task_done()
                    continue

            # expected record fields: 'date' and 'temp'
            date = record.get('date')
            temp = record.get('temp')
            # Place the processed tuple on the data queue for workers
            data_q.put((city, date, temp))
            cmd_q.task_done()
        except Exception:
            # Ensure task_done is called to avoid join deadlock
            try:
                cmd_q.task_done()
            except Exception:
                pass
            # keep processing other items
            continue


# ---------------------------------------------------------------------------
class Worker(threading.Thread):
    """
    Worker threaded class: consumes (city, date, temp) tuples from data_q
    and calls NOAA to store them.

    Expects sentinel None on data_q to exit.
    """

    def __init__(self, data_q, noaa, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_q = data_q
        self.noaa = noaa
        self.daemon = True

    def run(self):
        while True:
            item = self.data_q.get()
            try:
                if item is None:
                    self.data_q.task_done()
                    break
                city, date, temp = item
                # store the record in NOAA
                self.noaa.add_record(city, date, temp)
                self.data_q.task_done()
            except Exception:
                # ensure task_done to avoid deadlock
                try:
                    self.data_q.task_done()
                except Exception:
                    pass
                continue


# ---------------------------------------------------------------------------
class NOAA:
    """
    NOAA stores temperature data per city in a thread-safe manner and can
    compute average temperature for each city.
    """

    def __init__(self):
        # city -> list of temperatures
        self._data = {}
        # lock to protect _data
        self._lock = threading.Lock()
        # initialize lists for each city for predictable ordering and presence
        for city in CITIES:
            self._data[city] = []

    def add_record(self, city, date, temp):
        """
        Store a single temperature reading for a city.
        date included for completeness though not used in average calculation.
        """
        # Ensure temp is float
        try:
            t = float(temp)
        except Exception:
            # if temp is invalid, skip storing
            return
        with self._lock:
            if city not in self._data:
                self._data[city] = []
            self._data[city].append(t)

    def get_temp_details(self, city):
        """
        Return the average temperature for the given city.
        If no data exists, returns 0.0
        """
        with self._lock:
            temps = self._data.get(city, [])
            if not temps:
                return 0.0
            avg = sum(temps) / len(temps)
            return avg


# ---------------------------------------------------------------------------
def verify_noaa_results(noaa):

    answers = {
        'sandiego': 14.5004,
        'philadelphia': 14.865,
        'san_antonio': 14.638,
        'san_jose': 14.5756,
        'new_york': 14.6472,
        'houston': 14.591,
        'dallas': 14.835,
        'chicago': 14.6584,
        'los_angeles': 15.2346,
        'phoenix': 12.4404,
    }

    print()
    print('NOAA Results: Verifying Results')
    print('===================================')
    for name in CITIES:
        answer = answers[name]
        avg = noaa.get_temp_details(name)

        if abs(avg - answer) > 0.00001:
            msg = f'FAILED  Expected {answer}'
        else:
            msg = f'PASSED'
        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')


# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log='assignment.log')
    log.start_timer()

    noaa = NOAA()

    # Start server
    data = get_data_from_server(f'{TOP_API_URL}/start')

    # Get all cities number of records
    print('Retrieving city details')
    city_details = {}
    name = 'City'
    print(f'{name:>15}: Records')
    print('===================================')
    for name in CITIES:
        city_details[name] = get_data_from_server(f'{TOP_API_URL}/city/{name}')
        print(f'{name:>15}: Records = {city_details[name]["records"]:,}')
    print('===================================')

    records = RECORDS_TO_RETRIEVE

    # ---------------------------------------------------------------------
    # Create queues
    # cmd_q: main -> retriever threads (commands to fetch records)
    # data_q: retriever threads -> worker threads (retrieved record data)
    cmd_q = queue.Queue(maxsize=10)
    data_q = queue.Queue(maxsize=10)

    # Start worker threads
    workers = []
    for i in range(WORKERS):
        w = Worker(data_q, noaa, name=f'Worker-{i}')
        w.start()
        workers.append(w)

    # Start retrieval threads
    retrievers = []
    for i in range(THREADS):
        t = threading.Thread(target=retrieve_weather_data, args=(cmd_q, data_q), name=f'Retriever-{i}')
        t.daemon = True
        t.start()
        retrievers.append(t)

    # Enqueue commands: one task per record per city
    # Format: (city_name, record_number)
    for city in CITIES:
        for recno in range(records):
            cmd_q.put((city, recno))

    # Send sentinel None to retrieval threads so they will exit when queue emptied
    for _ in range(THREADS):
        cmd_q.put(None)

    # Wait until all commands have been processed by retrieval threads
    cmd_q.join()

    # At this point all retrieved records have been placed on data_q (or attempted)
    # Wait for retriever threads to finish
    for t in retrievers:
        t.join(timeout=1.0)

    # Send sentinel None to worker threads so they exit when done
    for _ in range(WORKERS):
        data_q.put(None)

    # Wait until workers finish processing all items
    data_q.join()

    # Ensure worker threads terminate
    for w in workers:
        w.join(timeout=1.0)

    # End server - don't change below
    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()
