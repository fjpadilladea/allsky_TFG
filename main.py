#!/usr/bin/env python3
from genericpath import isdir, isfile
import os
import argparse
import threading
import queue
import shutil
import csv
import detect_meteors as dm
import send_messages as sm

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
                        metavar=('meteors_directory', 'no_meteors_directory'),
                        help='move files to different directories depending on the results')
    parser.add_argument('-l', '--list',
                        metavar=('path'),
                        help='path of the txt results file')
    parser.add_argument('-s', '--send', action='store_true',
                        help='upload files with possible meteors to a Slack channel')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='analyse the content of the directory recursively')
    parser.add_argument('-csv', help='path of the csv results file')

    args = parser.parse_args()
    return args


def enqueue(source):
    """
    Recursively puts files in a queue for processing.

    Argument:
    source -- path of the file or directory to be enqueued.
    """
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
    """
    Processing of the files. Uses the detect function
    from the detect_meteors module.
    
    Argument:
    mask -- mask used to ignore regions of the input image
    """
    while True:
        file = proc_queue.get()
        print('Processing file: ', file)
        detection = dm.detect(file, mask)
        result = detection[0]
        lines = detection[1]
        # Put the file and the result in the postprocessing queue
        postproc_queue.put((file, result, lines))
        proc_queue.task_done()

def write_csv(file, lines, csv_file):
    """Writes rows with the file information in a .csv file"""
    # The path of the files follow the pattern:
    # camXX-location-CA-yyyy-mm-dd-hh-mm-ss/file.jpeg
    # Get the separator of the system
    fields = file.split(os.path.sep)
    # The last item of the path is the file
    file = fields[-1]
    # This information contains the rest of the information
    info = fields[-2]
    info = info.split('-')
    
    # Take information from original string
    camera = info[0]
    seconds = info[-1]
    minutes = info[-2]
    hours = info[-3]
    day = info[-5]
    month = info[-6]
    year = info[-7]

    # Leave only information relative to the location
    info.remove(camera)
    info.remove(seconds)
    info.remove(minutes)
    info.remove(hours)
    info.remove(day)
    info.remove(month)
    info.remove(year)
    info.remove('')

    # Get information about the location
    province = info[-1]

    info.remove(province)

    # Now the list contains only the specific place
    place = '-'.join(info)

    writer = csv.writer(csv_file)
    # The first element (ID) is left without nothing so it can auto-increment in a database
    data = ['',file,camera,place,province,year,month,day,hours,minutes,seconds,' '.join(str(line) for line in lines)]
    writer.writerow(data)

def postprocessing(list, move, send, csv_file):
    """Postprocessing of the files."""
    delimiter = ' - '
    if move is not None:
        meteors_dir = move[0]
        no_meteors_dir = move[1]
    while True:
        results = postproc_queue.get()
        print('Postprocessing file: ', results[0])

        # Generate the .txt results file        
        list.write(delimiter.join([str(results[0]), str(results[1])]))
        list.write(delimiter)
        if results[2] is not None:
            list.write(' '.join(str(line) for line in results[2]))
        else:
            list.write('None')
        list.write('\n')

        # .csv file
        if csv_file is not None:
            if results[1] is True:
                write_csv(results[0], results[2], csv_file)

        # Upload files with possible meteors to Slack
        if send is True:
            if results[1] is True:
                sm.upload(results[0])
        
        # Move files to different directories
        if move is not None:
            if results[1] is True:
                shutil.move(results[0], meteors_dir)

            elif results[1] is False:
                shutil.move(results[0], no_meteors_dir)

        postproc_queue.task_done()
        print('Completed file: ', results[0])

def main():
    args = parse_args()
    num_threads_proc = 10
    num_threads_postproc = 5

    # args is a Namespace object
    # vars() is used to manipulate it like a dictionary
    mask = vars(args)['mask']
    move = vars(args)['move']
    list = vars(args)['list']
    send = vars(args)['send']
    recursive = vars(args)['recursive']
    target_path = vars(args)['target']
    csv_path = vars(args)['csv']

    # Enqueue files
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

    # Create threads for processing    
    for t in range(num_threads_proc):
        t = threading.Thread(target=processing, args=(mask,), daemon=True)
        t.start()
    
    # Open results .txt file
    if list is None:
        list_file = open('results.txt', 'w')
    else:
        list_file = open(list, 'w')

    # Results .csv file
    if csv_path is not None:
        csv_file = open(csv_path, 'w', newline='') # newline = '' to avoid \n in the file
        writer = csv.writer(csv_file)
        # lines comes in the format (x1, y1, x2, y2)
        header = ['ID','file','cam','place','province','year','month','day','hour','minute','second','lines']
        writer.writerow(header)
    else:
        csv_file = None

    # Create threads for postprocessing
    for t_post in range(num_threads_postproc):
        t_post = threading.Thread(target=postprocessing, args=(list_file, move, send, csv_file) ,daemon=True)
        t_post.start()

    # Unblock program when all the files have been processed
    proc_queue.join()
    postproc_queue.join()

    # Close .txt results file
    list_file.close()

    # Close .csv file
    if csv_path is not None:
        csv_file.close()
    
    print('Analysis completed')

if __name__ == '__main__':
    main()