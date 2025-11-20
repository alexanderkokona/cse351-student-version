"""
Course: CSE 351 
Lesson: 10 Team
File:   team.py

Purpose: Hands-on experience with recursion, threads, processes,
         and observing how hardware behaves under different parallel models.

Instructions:
- DO NOT modify merge_sort(), merge_normal(), or any function marked "do not modify."
- Implement merge_sort_thread() and merge_sort_process() as recursive versions
  that use threading or multiprocessing at *each* recursive call.
"""

import time
import random
import threading
import multiprocessing as mp

from cse351 import *

# ---------------------------------------------------------------------------
# NORMAL MERGE SORT (DO NOT MODIFY)
# ---------------------------------------------------------------------------
def merge_sort(arr):
    """
    A standard merge sort implementation.
    DO NOT MODIFY THIS FUNCTION.
    """

    if len(arr) > 1:
        mid = len(arr) // 2

        L = arr[:mid]       # left half
        R = arr[mid:]       # right half

        merge_sort(L)       # sort left
        merge_sort(R)       # sort right

        i = j = k = 0

        # merge sorted halves
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1

        # finish remaining elements
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1


# ---------------------------------------------------------------------------
# Helper: Check if sorted (DO NOT MODIFY)
# ---------------------------------------------------------------------------
def is_sorted(arr):
    return all(arr[i] <= arr[i+1] for i in range(len(arr)-1))


# ---------------------------------------------------------------------------
# Wrapper for normal merge sort (DO NOT MODIFY)
# ---------------------------------------------------------------------------
def merge_normal(arr):
    merge_sort(arr)


# =========================================================================== 
# ========================= THREADED MERGE SORT ==============================
# ===========================================================================

def merge_sort_thread(arr):
    """
    A recursive merge sort that spawns *two threads* at each recursive call.
    This demonstrates high thread creation cost and GIL effects.
    """

    # Base case: lists of length 0–1 are already sorted
    if len(arr) > 1:

        # Find midpoint
        mid = len(arr) // 2

        # Split into two halves (these are normal Python lists)
        L = arr[:mid]
        R = arr[mid:]

        # --- Create threads for the recursive calls ---
        t1 = threading.Thread(target=merge_sort_thread, args=(L,))
        t2 = threading.Thread(target=merge_sort_thread, args=(R,))

        # Start both recursive tasks
        t1.start()
        t2.start()

        # Wait for both halves to finish sorting
        t1.join()
        t2.join()

        # --- Merge Phase ---
        i = j = k = 0

        # Merge sorted L and R back into arr
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1

        # Copy remaining elements of L
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1

        # Copy remaining elements of R
        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1


# =========================================================================== 
# ======================= PROCESS-BASED MERGE SORT ===========================
# ===========================================================================

def merge_sort_process(arr):
    """
    A recursive merge sort that spawns *two processes* per recursive call.
    Because processes do NOT share memory, we must use Manager().list()
    to allow sharing returned results.

    WARNING: This is extremely expensive but intentionally demonstrates
    process overhead and memory copying.
    """

    if len(arr) > 1:

        mid = len(arr) // 2

        # Split local array into halves
        L = arr[:mid]
        R = arr[mid:]

        # Create a Manager() so child processes can return data
        with mp.Manager() as manager:
            shared_L = manager.list(L)
            shared_R = manager.list(R)

            # Spawn child processes to sort the two halves
            p1 = mp.Process(target=merge_sort_process, args=(shared_L,))
            p2 = mp.Process(target=merge_sort_process, args=(shared_R,))

            # Start them
            p1.start()
            p2.start()

            # Wait for completion
            p1.join()
            p2.join()

            # Retrieve updated lists from shared memory
            L = list(shared_L)
            R = list(shared_R)

        # --- Merge Phase ---
        i = j = k = 0

        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1

        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1


# =========================================================================== 
# ============================ MAIN PROGRAM =================================
# ===========================================================================

def main():
    merges = [
        (merge_sort,        ' Normal Merge Sort '), 
        (merge_sort_thread, ' Threaded Merge Sort '), 
        (merge_sort_process,' Processes Merge Sort ')
    ]

    for merge_function, desc in merges:

        # Build array of 1,000,000 random numbers
        arr = [random.randint(1, 10_000_000) for _ in range(1_000_000)]

        print(f'\n{desc:-^70}')
        print(f'Before: {str(arr[:5])[1:-1]} ... {str(arr[-5:])[1:-1]}')

        # Time the sorting
        start = time.perf_counter()
        merge_function(arr)
        end = time.perf_counter()

        print(f'Sorted: {str(arr[:5])[1:-1]} ... {str(arr[-5:])[1:-1]}')

        print("Array is sorted" if is_sorted(arr) else "Array is NOT sorted")
        print(f'Time to sort = {end - start:.14f} seconds')


# Run main
if __name__ == '__main__':
    main()
