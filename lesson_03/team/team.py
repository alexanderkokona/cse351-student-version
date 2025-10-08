"""
Course: CSE 351 
Lesson: L03 team activity
File:   W03team-flair.py
Author: Alexander Kokona (with style ✨)

Purpose: Retrieve Star Wars details from a server (threaded, with flair!)
"""

import threading
import queue
import time
from common import *
from cse351 import *

# global
THREADS = 30
call_count = 0
print_lock = threading.Lock()

def worker(que, results):
    global call_count
    while True:
        url, category = que.get()
        if url is None:
            break

        call_count += 1
        data = get_data_from_server(url)
        with print_lock:
            print(f"   🌟 {category[:-1].capitalize()}: {data['name']}")
        results[category].append(data["name"])
        que.task_done()

def main():
    global call_count

    log = Log(show_terminal=True)
    log.start_timer("Starting to retrieve data from the server")

    print("\n====================================")
    print("   ⭐ STAR WARS DATA RETRIEVER ⭐   ")
    print("====================================\n")

    film6 = get_data_from_server(f"{TOP_API_URL}/films/6")
    call_count += 1
    print_dict(film6)

    # Shared queue
    que = queue.Queue()
    results = {cat: [] for cat in ["characters", "planets", "starships", "vehicles", "species"]}

    # Create and start threads
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker, args=(que, results))
        t.start()
        threads.append(t)

    # Fill queue with tasks
    for category in results.keys():
        print(f"\n🔎 Retrieving {category.capitalize()}...")
        start = time.time()
        for url in film6[category]:
            que.put((url, category))
        que.join()  # wait for category to finish
        elapsed = time.time() - start
        print(f"✅ {category.capitalize()} retrieved in {elapsed:.2f} sec")

    # Signal workers to exit
    for _ in range(THREADS):
        que.put((None, None))
    for t in threads:
        t.join()

    log.stop_timer("Total Time To complete")
    log.write(f"There were {call_count} calls to the server")

    # Final summary
    print("\n================== SUMMARY ==================")
    for cat, names in results.items():
        print(f"{cat.upper()} ({len(names)}):")
        for name in names[:5]:  # only show first 5 per category
            print(f"  - {name}")
        if len(names) > 5:
            print(f"  ... and {len(names)-5} more.")
    print("=============================================")

if __name__ == "__main__":
    main()
