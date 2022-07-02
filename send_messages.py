import shutil
import sys

def message(video):
    with open('log.txt', 'w') as log:
        log.write(str(video))

