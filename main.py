import numpy as np
import cv2
from collections import deque
import threading
import time
import rtmidi

midiout = rtmidi.MidiOut()

# Port 1 for loopMIDI
midiout.open_port(0)

#default called trackbar function
def setValues(x):
   print("")

def playnote(note=60):
    note_on = [0x90, note, 112] # channel 1, middle C, velocity 112
    note_off = [0x80, note, 0]
    midiout.send_message(note_on)
    time.sleep(0.1)
    midiout.send_message(note_off)
    time.sleep(0.1)


# Creating the trackbars needed for adjusting the marker colour
cv2.namedWindow("Color detectors")
cv2.createTrackbar("Upper Hue", "Color detectors", 69, 180,setValues)
cv2.createTrackbar("Upper Saturation", "Color detectors", 163, 255,setValues)
cv2.createTrackbar("Upper Value", "Color detectors", 255, 255,setValues)
cv2.createTrackbar("Lower Hue", "Color detectors", 20, 180,setValues)
cv2.createTrackbar("Lower Saturation", "Color detectors", 59, 255,setValues)
cv2.createTrackbar("Lower Value", "Color detectors", 194, 255,setValues)

#The kernel to be used for dilation purpose
kernel = np.ones((5,5),np.uint8)

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0

#Resizing the frame

def rescaleframe(frame,scale=2):
        width = int(frame.shape[1] + scale)
        height = int(frame.shape[0] + scale)

        dimensions = (width,height)

        return cv2.resize(frame , dimensions , interpolation=cv2.INTER_AREA)
        
# Loading the default webcam of PC.
cap = cv2.VideoCapture(0)
d = deque([48])
track = 80

# Keep looping
while True:

    if(len(d)!=0):
        t = threading.Thread(target=playnote, args=(d.popleft(),))
        t.start()

    # Reading the frame from the camera
    ret, frame = cap.read()
    #Flipping the frame to see same side of yours
    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


    u_hue = cv2.getTrackbarPos("Upper Hue", "Color detectors")
    u_saturation = cv2.getTrackbarPos("Upper Saturation", "Color detectors")
    u_value = cv2.getTrackbarPos("Upper Value", "Color detectors")
    l_hue = cv2.getTrackbarPos("Lower Hue", "Color detectors")
    l_saturation = cv2.getTrackbarPos("Lower Saturation", "Color detectors")
    l_value = cv2.getTrackbarPos("Lower Value", "Color detectors")
    Upper_hsv = np.array([u_hue,u_saturation,u_value])
    Lower_hsv = np.array([l_hue,l_saturation,l_value])


    # Adding the colour buttons to the live frame for colour access
    frame = cv2.rectangle(frame, (80,1), (160,80), (122,122,122), -1)
    frame = cv2.rectangle(frame, (175,1), (255,80), colors[0], -1)
    frame = cv2.rectangle(frame, (270,1), (350,80), colors[1], -1)
    frame = cv2.rectangle(frame, (365,1), (445,80), colors[2], -1)
    frame = cv2.rectangle(frame, (460,1), (540,80), colors[3], -1)

    frame = cv2.rectangle(frame, (1,80), (80,160), colors[3], -1)
    frame = cv2.rectangle(frame, (1,175), (80,255), colors[2], -1)
    frame = cv2.rectangle(frame, (1,270), (80,350), colors[1], -1)
    frame = cv2.rectangle(frame, (1,365), (80,445), colors[0], -1)



    cv2.putText(frame, "Pat.1", (96, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "Pat.2", (190, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Pat.3", (290, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Pat.4", (380, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Pat.5", (480, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 2, cv2.LINE_AA)
    
    cv2.putText(frame, "TRACK 1", (8, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, "TRACK 2", (8, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "TRACK 3", (8, 305), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "TRACK 4", (8, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Identifying the pointer by making its mask
    Mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
    Mask = cv2.erode(Mask, kernel, iterations=1)
    Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, kernel)
    Mask = cv2.dilate(Mask, kernel, iterations=1)

    # Find contours for the pointer after idetifying it
    cnts,_ = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,
    	cv2.CHAIN_APPROX_SIMPLE)
    center = None
    # If the contours are formed
    if len(cnts) > 0:
    	# sorting the contours to find biggest
        cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
        # Get the radius of the enclosing circle around the found contour
        ((x, y), radius) = cv2.minEnclosingCircle(cnt)
        # Draw the circle around the contour
        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
        # Calculating the center of the detected contour
        M = cv2.moments(cnt)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        # Now checking if the user wants to click on any button above the screen
        if center[0] <= 80:
            if 80 <= center[0] <= 160:
                track=80

            elif 175 <= center[0] <= 255:
                track=70

            elif 270 <= center[0] <= 350:
                track=60

            elif 365 <= center[0] <= 445:
                track=50

        if center[1] <= 80:

            if 80 <= center[0] <= 160: # Clear Button

                if(len(d)==0):
                    t.join()
                    d.append(track+1)

            elif 175 <= center[0] <= 255:
                    colorIndex = 0 # Blue
                    if(len(d)==0):
                        t.join()
                        d.append(track+2)
            elif 270 <= center[0] <= 350:
                    colorIndex = 1 # Green
                    if(len(d)==0):
                        t.join()
                        d.append(track+3)
            elif 460 <= center[0] <= 540:

                    if(len(d)==0):
                        t.join()
                        d.append(track+4)
            elif 505 <= center[0] <= 600:

                    if(len(d)==0):
                        t.join()
                        d.append(track+9)
#RESIZE
    frame_rs=rescaleframe(frame)


    # Show all the windows
    cv2.imshow("Tracking", frame)
    cv2.imshow("resize",frame_rs)
    cv2.imshow("mask",Mask)

    

	# If the 'q' key is pressed then stop the application
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the camera and all resources
cap.release()
cv2.destroyAllWindows()

