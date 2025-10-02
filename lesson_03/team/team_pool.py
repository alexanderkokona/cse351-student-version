"""
Course: CSE 351 
Lesson: L03 team activity
File:   team.py
Author: <Add name here>

Purpose: Retrieve Star Wars details from a server

Instructions:

- This program requires that the server.py program be started in a terminal window.
- The program will retrieve the names of:
    - characters
    - planets
    - starships
    - vehicles
    - species

- the server will delay the request by 0.5 seconds

TODO
- Create a threaded function to make a call to the server where
  it retrieves data based on a URL.  The function should have a method
  called get_name() that returns the name of the character, planet, etc...
- The threaded function should only retrieve one URL.
- Create a queue that will be used between the main thread and the threaded functions

- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""

from datetime import datetime, timedelta
import threading
from common import *

# Include cse 351 common Python files
from cse351 import *

# global
call_count = 0

class request(threading.Thread):
    def __init__(self, url:str):
        super().__init__()

    


def get_urls(film6, kind):
    global call_count

    urls = film6[kind]
    print(kind)
    for url in urls:
        #call_count += 1
        #item = get_data_from_server(url)
        #print(f'  - {item['name']}')
        t = request
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


    print_lock.aquire()
    print(kind)
    for t in threads:
        print(f' - {t.name}', flush=True)
    print.lock.release()

def main():
    global call_count

    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    film6 = get_data_from_server(f'{TOP_API_URL}/films/6')
    call_count += 1
    print_dict(film6)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        print_lock = threading.Lock()
        executor.map(start_getting_urls, [(film6, print_lock, 'characters'), 
                                          (film6, print_lock, 'planets'), 
                                          (film6, print_lock, 'starships'), 
                                          (film6, print_lock, 'vehicles'), 
                                          (film6, print_lock, 'species')])

    # Retrieve people
    # threads = [threading.Thread(target=geturls, args=(film6, x, print_lock)) for x in ['characters', 'planets', 'starships', 'vehicles', 'species']]
    # get_urls(film6, 'characters')
    # get_urls(film6, 'planets')
    # get_urls(film6, 'starships')
    # get_urls(film6, 'vehicles')
    # get_urls(film6, 'species')
    #for t in threads:
    #    t.start()
    #for t in threads:
    #    t.join()

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')

if __name__ == "__main__":
    main()
