"""
Course: CSE 351
Assignment: 06
Author: Alexander Kokona

Instructions:

- see instructions in the assignment description in Canvas

""" 

import multiprocessing as mp
import os
import cv2
import numpy as np

from cse351 import *

# Folders
INPUT_FOLDER = "faces"
STEP1_OUTPUT_FOLDER = "step1_smoothed"
STEP2_OUTPUT_FOLDER = "step2_grayscale"
STEP3_OUTPUT_FOLDER = "step3_edges"

# Parameters for image processing
GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)
CANNY_THRESHOLD1 = 75
CANNY_THRESHOLD2 = 155

# Allowed image extensions
ALLOWED_EXTENSIONS = ['.jpg']

# ---------------------------------------------------------------------------
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

# ---------------------------------------------------------------------------
def task_convert_to_grayscale(image):
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        return image # Already grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# ---------------------------------------------------------------------------
def task_smooth_image(image, kernel_size):
    return cv2.GaussianBlur(image, kernel_size, 0)

# ---------------------------------------------------------------------------
def task_detect_edges(image, threshold1, threshold2):
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(image, threshold1, threshold2)

# ---------------------------------------------------------------------------
def worker_smooth(que_in, que_out):
    while True:
        item = que_in.get()
        if item is None:
            que_out.put(None)
            break
        infile, outfile = item
        img = cv2.imread(infile)
        if img is not None:
            smoothed = task_smooth_image(img, GAUSSIAN_BLUR_KERNEL_SIZE)
            que_out.put((smoothed, outfile))

# ---------------------------------------------------------------------------
def worker_grayscale(que_in, que_out):
    while True:
        item = que_in.get()
        if item is None:
            que_out.put(None)
            break
        img, outfile = item
        gray = task_convert_to_grayscale(img)
        que_out.put((gray, outfile))

# ---------------------------------------------------------------------------
def worker_edges(que_in):
    while True:
        item = que_in.get()
        if item is None:
            break
        img, outfile = item
        edges = task_detect_edges(img, CANNY_THRESHOLD1, CANNY_THRESHOLD2)
        cv2.imwrite(outfile, edges)

# ---------------------------------------------------------------------------
def run_image_processing_pipeline():
    print("Starting image processing pipeline...")

    create_folder_if_not_exists(STEP1_OUTPUT_FOLDER)
    create_folder_if_not_exists(STEP2_OUTPUT_FOLDER)
    create_folder_if_not_exists(STEP3_OUTPUT_FOLDER)

    # List all images
    files = [f for f in os.listdir(INPUT_FOLDER) if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS]

    # Create queues
    que1 = mp.Queue(maxsize=50)
    que2 = mp.Queue(maxsize=50)
    que3 = mp.Queue(maxsize=50)

    # Add initial images to queue1
    for f in files:
        infile = os.path.join(INPUT_FOLDER, f)
        outfile = os.path.join(STEP3_OUTPUT_FOLDER, f)  # Final edge image path
        que1.put((infile, outfile))

    # Add sentinel values
    num_processes = mp.cpu_count()
    for _ in range(num_processes):
        que1.put(None)

    # Start worker processes
    smooth_procs = [mp.Process(target=worker_smooth, args=(que1, que2)) for _ in range(num_processes)]
    gray_procs = [mp.Process(target=worker_grayscale, args=(que2, que3)) for _ in range(num_processes)]
    edge_procs = [mp.Process(target=worker_edges, args=(que3,)) for _ in range(num_processes)]

    for p in smooth_procs + gray_procs + edge_procs:
        p.start()

    # Wait for all processes to finish
    for p in smooth_procs + gray_procs + edge_procs:
        p.join()

    print("\nImage processing pipeline finished!")
    print(f"Original images are in: '{INPUT_FOLDER}'")
    print(f"Edge images are in: '{STEP3_OUTPUT_FOLDER}'")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer('Processing Images')

    # check for input folder
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The input folder '{INPUT_FOLDER}' was not found.")
        print(f"Create it and place your face images inside it.")
        print('Link to faces.zip:')
        print('   https://drive.google.com/file/d/1eebhLE51axpLZoU6s_Shtw1QNcXqtyHM/view?usp=sharing')
    else:
        run_image_processing_pipeline()

    log.write()
    log.stop_timer('Total Time To complete')
