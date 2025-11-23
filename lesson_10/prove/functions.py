"""
Course: CSE 351, week 10
File: functions.py
Author: <your name>

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
family_id = 6128784944
data = get_data_from_server('{TOP_API_URL}/family/{family_id}')

Example JSON returned from the server
{
    'id': 6128784944, 
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
person_id = 2373686152
data = get_data_from_server('{TOP_API_URL}/person/{person_id}')

Example JSON returned from the server
{
    'id': 2373686152, 
    'name': 'Stella', 
    'birth': '9-3-1846', 
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}


--------------------------------------------------------------------------------------
You will lose 10% if you don't detail your part 1 and part 2 code below

Describe how to speed up part 1

Part 1 uses a **recursive DFS** over families. Each family is fetched from the
`/family/<id>` API, then all related people (husband, wife, children) are fetched
from `/person/<id>`. To speed it up, I:
- Keep shared `visited_families` and `visited_people` sets so I never fetch the
  same family or person twice.
- Protect the shared `Tree` and the visited sets with locks so multiple threads
  can safely add data.
- Use recursion for the DFS structure, but whenever I discover a parent family
  (via `person.parent_id`), I start a **new thread** that continues the DFS up
  that branch. This overlaps the 0.25-second server latency for many requests
  at once instead of waiting for each call sequentially.
- At the end, I join all spawned threads so the function finishes only after
  the full pedigree has been retrieved.


Describe how to speed up part 2

Part 2 uses a **Breadth-First Search (BFS)** over families, level by level,
without recursion:
- I keep a `current_level` list of family IDs. For each level, I spawn one
  worker thread per family (unlimited count for speed).
- Each worker fetches the family and all of its people and adds them to the
  shared `Tree` under a lock.
- While processing, workers collect the next level of ancestor families using
  the parents of the husband and wife (`person.parent_id`) and store them in a
  shared `next_level` set (also under a lock) so there are no duplicates.
- When all threads for the current level finish, I move `next_level` into
  `current_level` and repeat.
This gives a clear BFS (level-by-level) structure and overlaps many server
requests concurrently for maximum throughput.


Extra (Optional) 10% Bonus to speed up part 3

Part 3 uses the same BFS, but I explicitly **limit concurrency to 5 threads**
so the server never has more than 5 active request threads from this client:
- I still do BFS by levels, but I process each level in **chunks of at most 5
  families at a time**.
- For each chunk, I start up to 5 worker threads, wait (join) for them to
  finish, and then move to the next chunk.
- Because each worker performs its HTTP calls sequentially, and there are never
  more than 5 active workers, the server will not see more than 5 concurrent
  requests while the program runs, while still trying to keep 5 active as much
  as possible.
"""

from common import *
import queue
import threading


# ----------------------------------------------------------------------------- #
# Helper functions (no try/except here; all error handling is inside common.py) #
# ----------------------------------------------------------------------------- #

def _fetch_family_data(family_id):
    """Fetch a family JSON safely. Returns None if the server did not provide a valid family."""
    if family_id is None or family_id == 0:
        return None

    url = f'{TOP_API_URL}/family/{family_id}'

    # get_data_from_server already retries and handles exceptions.
    data = get_data_from_server(url)

    # Handle empty / invalid JSON gracefully.
    if not data or 'id' not in data:
        return None

    return data


def _fetch_person_data(person_id):
    """Fetch a person JSON safely. Returns None if the server did not provide a valid person."""
    if person_id is None or person_id == 0:
        return None

    url = f'{TOP_API_URL}/person/{person_id}'
    data = get_data_from_server(url)

    if not data or 'id' not in data:
        return None

    return data


# ----------------------------------------------------------------------------- #
# Part 1 – Depth-First Search pedigree (recursive, threaded)                    #
# ----------------------------------------------------------------------------- #

def depth_fs_pedigree(family_id, tree):
    # KEEP this function even if you don't implement it
    # DFS with recursion + threads: each parent branch runs in its own thread.

    tree_lock = threading.Lock()
    family_lock = threading.Lock()
    visited_families = set()
    visited_people = set()

    threads = []
    threads_lock = threading.Lock()

    def register_thread(t):
        with threads_lock:
            threads.append(t)

    def add_family_to_tree(fam_obj):
        with tree_lock:
            if not tree.does_family_exist(fam_obj.get_id()):
                tree.add_family(fam_obj)

    def add_person_to_tree(person_obj):
        with tree_lock:
            if not tree.does_person_exist(person_obj.get_id()):
                tree.add_person(person_obj)

    def dfs_family(current_family_id):
        # Depth-first traversal of the pedigree using recursion.
        with family_lock:
            if current_family_id in visited_families:
                return
            visited_families.add(current_family_id)

        fam_data = _fetch_family_data(current_family_id)
        if fam_data is None:
            return

        family = Family(fam_data)
        add_family_to_tree(family)

        # Collect all relevant person IDs in this family.
        person_ids = []

        husband_id = family.get_husband()
        if husband_id is not None and husband_id != 0:
            person_ids.append(husband_id)

        wife_id = family.get_wife()
        if wife_id is not None and wife_id != 0:
            person_ids.append(wife_id)

        for child_id in family.get_children():
            if child_id is not None and child_id != 0:
                person_ids.append(child_id)

        # Process all people in this family.
        for pid in person_ids:
            with tree_lock:
                if pid in visited_people:
                    continue
                visited_people.add(pid)

            person_data = _fetch_person_data(pid)
            if person_data is None:
                continue

            person = Person(person_data)
            add_person_to_tree(person)

            # DFS step: move up to this person's parents (parent family).
            parent_family_id = person.get_parentid()
            if parent_family_id is None or parent_family_id == 0:
                continue

            # Only start a new DFS thread if we haven't seen this family yet.
            with family_lock:
                already_seen = parent_family_id in visited_families

            if not already_seen:
                t = threading.Thread(target=dfs_family, args=(parent_family_id,))
                register_thread(t)
                t.start()

    # Start DFS from the starting family in its own thread.
    root_thread = threading.Thread(target=dfs_family, args=(family_id,))
    register_thread(root_thread)
    root_thread.start()

    # Wait for all spawned DFS threads to finish.
    # Because threads can spawn new threads, we loop until no new threads are created.
    while True:
        with threads_lock:
            snapshot = list(threads)
        for t in snapshot:
            t.join()
        with threads_lock:
            if len(threads) == len(snapshot):
                break


# ----------------------------------------------------------------------------- #
# Part 2 – Breadth-First Search pedigree (fast as possible, many threads)       #
# ----------------------------------------------------------------------------- #

def breadth_fs_pedigree(family_id, tree):
    # KEEP this function even if you don't implement it
    # BFS – no recursion, level by level, with many threads per level.

    tree_lock = threading.Lock()
    family_lock = threading.Lock()
    visited_families = set()
    visited_people = set()

    # Start BFS with the initial family.
    current_level = [family_id]

    def add_family_to_tree(fam_obj):
        with tree_lock:
            if not tree.does_family_exist(fam_obj.get_id()):
                tree.add_family(fam_obj)

    def add_person_to_tree(person_obj):
        with tree_lock:
            if not tree.does_person_exist(person_obj.get_id()):
                tree.add_person(person_obj)

    # Standard BFS loop: process one generation (level) at a time.
    while current_level:
        threads = []
        next_level_set = set()
        next_level_lock = threading.Lock()

        def worker_process_family(current_family_id):
            # Mark family visited (BFS node visit).
            with family_lock:
                if current_family_id in visited_families:
                    return
                visited_families.add(current_family_id)

            fam_data = _fetch_family_data(current_family_id)
            if fam_data is None:
                return

            family = Family(fam_data)
            add_family_to_tree(family)

            person_ids = []

            husband_id = family.get_husband()
            if husband_id is not None and husband_id != 0:
                person_ids.append(husband_id)

            wife_id = family.get_wife()
            if wife_id is not None and wife_id != 0:
                person_ids.append(wife_id)

            for child_id in family.get_children():
                if child_id is not None and child_id != 0:
                    person_ids.append(child_id)

            # Process all people in this family (fetch and add).
            parent_families_for_this_family = []

            for pid in person_ids:
                with tree_lock:
                    if pid in visited_people:
                        continue
                    visited_people.add(pid)

                person_data = _fetch_person_data(pid)
                if person_data is None:
                    continue

                person = Person(person_data)
                add_person_to_tree(person)

                parent_family_id = person.get_parentid()
                if parent_family_id is not None and parent_family_id != 0:
                    parent_families_for_this_family.append(parent_family_id)

            # Collect parent families into the next level (BFS frontier expansion).
            if parent_families_for_this_family:
                with next_level_lock:
                    for pfid in parent_families_for_this_family:
                        if pfid not in visited_families:
                            next_level_set.add(pfid)

        # Spawn one worker thread per family in this BFS level.
        for fid in current_level:
            t = threading.Thread(target=worker_process_family, args=(fid,))
            threads.append(t)
            t.start()

        # Wait for all workers in this level to finish.
        for t in threads:
            t.join()

        # Next BFS level: convert set to list.
        current_level = list(next_level_set)


# ----------------------------------------------------------------------------- #
# Part 3 – Breadth-First Search pedigree, limited to 5 concurrent threads       #
# ----------------------------------------------------------------------------- #

def breadth_fs_pedigree_limit5(family_id, tree):
    # KEEP this function even if you don't implement it
    # BFS – no recursion, but now we enforce a hard limit of 5 concurrent threads.

    MAX_WORKERS = 5

    tree_lock = threading.Lock()
    family_lock = threading.Lock()
    visited_families = set()
    visited_people = set()

    current_level = [family_id]

    def add_family_to_tree(fam_obj):
        with tree_lock:
            if not tree.does_family_exist(fam_obj.get_id()):
                tree.add_family(fam_obj)

    def add_person_to_tree(person_obj):
        with tree_lock:
            if not tree.does_person_exist(person_obj.get_id()):
                tree.add_person(person_obj)

    while current_level:
        next_level_set = set()
        next_level_lock = threading.Lock()

        # We will process this level in chunks of up to MAX_WORKERS families.
        index = 0
        level_size = len(current_level)

        def worker_process_family(current_family_id):
            with family_lock:
                if current_family_id in visited_families:
                    return
                visited_families.add(current_family_id)

            fam_data = _fetch_family_data(current_family_id)
            if fam_data is None:
                return

            family = Family(fam_data)
            add_family_to_tree(family)

            person_ids = []

            husband_id = family.get_husband()
            if husband_id is not None and husband_id != 0:
                person_ids.append(husband_id)

            wife_id = family.get_wife()
            if wife_id is not None and wife_id != 0:
                person_ids.append(wife_id)

            for child_id in family.get_children():
                if child_id is not None and child_id != 0:
                    person_ids.append(child_id)

            parent_families_for_this_family = []

            for pid in person_ids:
                with tree_lock:
                    if pid in visited_people:
                        continue
                    visited_people.add(pid)

                person_data = _fetch_person_data(pid)
                if person_data is None:
                    continue

                person = Person(person_data)
                add_person_to_tree(person)

                parent_family_id = person.get_parentid()
                if parent_family_id is not None and parent_family_id != 0:
                    parent_families_for_this_family.append(parent_family_id)

            if parent_families_for_this_family:
                with next_level_lock:
                    for pfid in parent_families_for_this_family:
                        if pfid not in visited_families:
                            next_level_set.add(pfid)

        # Process the current level in waves of up to MAX_WORKERS threads.
        while index < level_size:
            threads = []
            # Choose the next chunk of families to process concurrently.
            chunk = current_level[index:index + MAX_WORKERS]

            for fid in chunk:
                t = threading.Thread(target=worker_process_family, args=(fid,))
                threads.append(t)
                t.start()

            # Wait until this chunk finishes before starting the next one.
            for t in threads:
                t.join()

            index += MAX_WORKERS

        # Move on to the next BFS level.
        current_level = list(next_level_set)
