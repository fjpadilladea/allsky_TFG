#!/usr/bin/env python3
from genericpath import isdir, isfile
import os
import argparse
import threading
import queue
import shutil
import test_detect_meteors as dm
import test_send_messages as sm

import time

proc_queue = queue.Queue()
postproc_queue = queue.Queue()

def parse_args():
    """Parse the arguments passed in the command line."""
    parser = argparse.ArgumentParser(description='Meteor detection software',
                                    epilog='FJPDA 2022',)

    parser.add_argument('target', help='target file or directory to process')
    parser.add_argument('-m', '--mask', default=None,
                        help='.pgm image used as mask for processing')
    
    parser.add_argument('-mv', '--move', nargs=2,
                        metavar=('meteors_directory', 'no_meteors_directory'))
    parser.add_argument('-l', '--list',
                        metavar=('path'))
    parser.add_argument('-s', '--send', action='store_true')
    parser.add_argument('-r', '--recursive', action='store_true')

    args = parser.parse_args()
    return args


def enqueue(source):
    """Recursively puts files in a queue for processing."""
    if os.path.isfile(source):
        proc_queue.put(source)

    elif os.path.isdir(source):

        # List the content of the origin directory
        content = os.listdir(source)

        for element in content:
            # To have the complete path at all times
            path = os.path.join(source, element)
            enqueue(path)

def processing(mask):
    """Processing of the files."""
    while True:
        file = proc_queue.get()
        # print('Processing ', file)
        # Cuando sea real, con OpenCV:
        # Comprobar si hay una detección o no, si hay
        # una detección, poner el elemento en la queue
        # de postproc
        # Idea para mv: pasar a la queue de posproc una tuple
        # que sea (file, yes/no), y dependiendo del segundo
        # elemento moverlo a un dir o a otro
        # print(file, mask)
        result = dm.detect(file, mask)
        # print(file, result)
        postproc_queue.put((file, result))
        proc_queue.task_done()

def postprocessing(list, move, send):
    """Postprocessing of the files"""
    delimiter = ' - '
    if move is not None:
        meteors_dir = move[0]
        no_meteors_dir = move[1]
    while True:
        results = postproc_queue.get()
        
        list.write(delimiter.join([str(element) for element in results]))
        list.write('\n')

        if send is True:
            if results[1] is True:
                sm.upload(results[0])
        
        if move is not None:
            if results[1] is True:
                shutil.move(results[0], meteors_dir)

            elif results[1] is False:
                shutil.move(results[0], no_meteors_dir)

        postproc_queue.task_done()

def main():
    start = time.time()
    args = parse_args()
    num_threads = 5
    
    # args is a Namespace object
    # vars() is used to manipulate it like a dictionary
    mask = vars(args)['mask']
    move = vars(args)['move']
    list = vars(args)['list']
    send = vars(args)['send']
    recursive = vars(args)['recursive']
    target_path = vars(args)['target']

    if recursive is True:
        enqueue(target_path)

    elif os.path.isfile(target_path):
        proc_queue.put(target_path)

    elif os.path.isdir(target_path):
        content = os.listdir(target_path)

        for element in content:
            path = os.path.join(target_path, element)

            if os.path.isfile(path):
                proc_queue.put(path)
    
    for t in range(num_threads):
        t = threading.Thread(target=processing, args=(mask,), daemon=True)
        t.start()
    
    if list is None:
        list_file = open('results.txt', 'w')
    else:
        list_file = open(list, 'w')
    
    t_list = threading.Thread(target=postprocessing, args=(list_file, move, send) ,daemon=True)
    t_list.start()

    proc_queue.join()
    postproc_queue.join()

    list_file.close()

    elapsed = time.time() - start
    print(elapsed)


if __name__ == '__main__':
    main()