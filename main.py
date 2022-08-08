#!/usr/bin/env python3
import sys
import shutil
import os
import detect_meteors as dm
import send_messages as sm

sys.stderr = open('error_log.txt', 'w')
sys.stdout = open('out.txt', 'w')
print("Executed")

output_dir = sys.argv[1] + '/'
meteorsDir = sys.argv[2] + '/'
notMeteorsDir = sys.argv[3] + '/'
mask_image = sys.argv[4]

# Check if the video has meteors
for vid in os.listdir(output_dir):
    video = output_dir + vid
    meteorFound = dm.detect(video, mask_image)
    
    sm.message(video)

    # Move to different directories
    if meteorFound == True:
        shutil.move(video, meteorsDir)
        print('Meteor found: ' + vid)
    else:
        shutil.move(video, notMeteorsDir)
        print('Not a meteor: ' + vid)
