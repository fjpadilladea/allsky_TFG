import cv2 as cv
import numpy as np
import os

def img_processing(img, mask):
    """
    Processing of a single image.
    Arguments:
    img -- image to be processed
    mask -- mask used to ignore regions of the input image

    Returns:
    True or False depending if a possible meteor is detected
    """
    # Blur image (decrease sensibility)
    blurred = cv.GaussianBlur(img,(17,17),0)
    
    # Find edges using Canny's algorithm
    edges = cv.Canny(blurred,100,200)
    
    # Closing (dilation - erosion)
    closed = cv.morphologyEx(edges, cv.MORPH_CLOSE, (7,7), iterations = 5)
    
    # Masking
    masked = cv.bitwise_and(closed, mask)
    
    # Find lines using Hough Lines Transform
    # The function returns None if there are no lines found
    lines = cv.HoughLinesP(masked,1,np.pi/180,30,minLineLength=20,maxLineGap=10)
    
    # Lines are considered as possible meteors
    # If a line is found, return True. Otherwise, return False
    if lines is not None:
        return True
    else:
        return False

def detect(file, mask_image):
    """
    Processes the input file searching for meteors.
    img_processing() function is called.

    Arguments:
    file -- image or video to be processed
    mask -- mask used to ignore regions of the input image

    Returns:
    True or False depending if a possible meteor is detected
    """
    if mask_image is None:
    # If a mask image is not passed as an argument,
    # use a white image as the mask
        mask = np.ones((1,1,1),dtype=np.uint8)*255
    else:
     # Read the mask file
    # It is necessary to open it as a grayscale image in order to do de bitwise AND operation
    # between the mask and the 'closed' image, which has only one channel
        mask = cv.imread(mask_image, cv.IMREAD_GRAYSCALE)    
    
    # Check file extension
    split_name = os.path.splitext(file)
    extension = split_name[1]
    
    # If the file is an image
    if extension == '.jpeg' or extension == '.jpg' or extension == '.png':
        img = cv.imread(file)
        
        #Resize the mask
        dimensions = img.shape
        height = dimensions[0]
        width = dimensions[1]
        resizedMask = cv.resize(mask, (width,height), interpolation = cv.INTER_AREA)
        
        detection = img_processing(img, resizedMask)
        # If a meteor is detected, return True. Otherwise, return False
        if detection == True:
            return True
        else:
            return False 
    
    # If the file is a video
    elif extension == '.mp4' or extension == '.avi':
        vid = cv.VideoCapture(file)
        
        if (vid.isOpened() == False):
            print('Error opening video ' + file)

        while(vid.isOpened()):
        
            # Get the next frame of the video
            ret, frame = vid.read()
        
            # If there are more frames available
            if ret == True:
                # Resize the mask
                dimensions = frame.shape
                height = dimensions[0]
                width = dimensions[1]
                resizedMask = cv.resize(mask, (width,height), interpolation = cv.INTER_AREA)
                
                detection = img_processing(frame)

                # If a meteor is detected, close the video file and return True
                if detection is True:
                    vid.release()
                    return True
                
            # If there are no more frames in the video, break out of the loop
            else:
                break

        # Release video capture
        vid.release()
        
        # No meteors were detected: return False
        return False
