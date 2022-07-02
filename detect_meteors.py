import cv2 as cv
import numpy as np

def detect(video, mask_image):

    vid = cv.VideoCapture(video)
    
    if (vid.isOpened() == False):
        print('Error opening video ' + video)
    
    # Read the mask file
    # It is necessary to open it as a grayscale image in order to do de bitwise AND operation
    # between the mask and the 'closed' image, which has only one channel
    mask = cv.imread(mask_image, cv.IMREAD_GRAYSCALE)
    
    # Resize the mask
    resizedMask = cv.resize(mask, (1920,1080), interpolation = cv.INTER_AREA)

    while(vid.isOpened()):
    
        # Get the next frame of the video
        ret, frame = vid.read()
    
        # If there are more frames available
        if ret == True:
            
            # Resize image
            resized = cv.resize(frame, (1920,1080), interpolation = cv.INTER_AREA)
            
            # Blur image (decrease sensibility)
            blurred = cv.GaussianBlur(resized,(17,17),0)
            
            # Find edges using Canny's algorithm
            edges = cv.Canny(blurred,100,200)
            
            # Closing (dilation - erosion)
            closed = cv.morphologyEx(edges, cv.MORPH_CLOSE, (7,7), iterations = 5)
            
            # Masking
            masked = cv.bitwise_and(closed, resizedMask)
            
            # Find lines using Hough Lines Transform
            # The function returns None if there are no lines found
            lines = cv.HoughLinesP(masked,1,np.pi/180,30,minLineLength=20,maxLineGap=10)
            
            # If a meteor is detected, return True
            if lines is not None:
                vid.release()
                return True
            

        # If there are no more frames in the video, break out of the loop
        else:
            break

    # Release video capture
    vid.release()
    
    # No meteors were detected: return False
    return False
    
