import numpy as np
import cv2
from collections import deque
import threading
import time
import rtmidi
import json

f = open('object.json')
data = json.load(f)
obj = data["highlighter"]

midiout = rtmidi.MidiOut()

# Port 1 for loopMIDI
midiout.open_port(1)

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
cv2.createTrackbar("Upper Hue", "Color detectors", obj[0], 180,setValues)
cv2.createTrackbar("Upper Saturation", "Color detectors", obj[1], 255,setValues)
cv2.createTrackbar("Upper Value", "Color detectors", obj[2], 255,setValues)
cv2.createTrackbar("Lower Hue", "Color detectors", obj[3], 180,setValues)
cv2.createTrackbar("Lower Saturation", "Color detectors", obj[4], 255,setValues)
cv2.createTrackbar("Lower Value", "Color detectors", obj[5], 255,setValues)

#The kernel to be used for dilation purpose
kernel = np.ones((5,5),np.uint8)

# colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
grey = (122,122,122)
green = (0, 255, 0)

pat1 = grey
pat2 = grey
pat3 = grey
pat4 = grey
pat5 = grey


track1 = grey
track2 = grey
track3 = grey
track4 = grey

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
    # Patterns
    frame = cv2.rectangle(frame, (80,1), (160,80), pat1, -1)
    frame = cv2.rectangle(frame, (175,1), (255,80), pat2, -1)
    frame = cv2.rectangle(frame, (270,1), (350,80), pat3, -1)
    frame = cv2.rectangle(frame, (365,1), (445,80), pat4, -1)
    frame = cv2.rectangle(frame, (460,1), (540,80), pat5, -1)

    # Tracks
    frame = cv2.rectangle(frame, (1,80), (80,160), track1, -1)
    frame = cv2.rectangle(frame, (1,175), (80,255), track2, -1)
    frame = cv2.rectangle(frame, (1,270), (80,350), track3, -1)
    frame = cv2.rectangle(frame, (1,365), (80,445), track4, -1)



    cv2.putText(frame, "Pat.1", (96, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "Pat.2", (190, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "Pat.3", (290, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "Pat.4", (380, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "MUTE", (480, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.putText(frame, "TRACK 1", (8, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "TRACK 2", (8, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "TRACK 3", (8, 305), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "TRACK 4", (8, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

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
        # Tracks
        if center[0] <= 80:
            if 80 <= center[1] <= 160:
                track=80
                track1 = green
                track2 = grey
                track3 = grey
                track4 = grey

            elif 175 <= center[1] <= 255:
                track=70
                track2 = green
                track1 = grey
                track3 = grey
                track4 = grey

            elif 270 <= center[1] <= 350:
                track=60
                track3 = green
                track2 = grey
                track1 = grey
                track4 = grey

            elif 365 <= center[1] <= 445:
                track=50
                track4 = green
                track2 = grey
                track3 = grey
                track1 = grey

        if center[1] <= 80:

            if 80 <= center[0] <= 160:
                if(len(d)==0):
                    t.join()
                    d.append(track+1)
                    pat1=green
                    pat2=grey
                    pat3=grey
                    pat4=grey
                    pat5=grey


            elif 175 <= center[0] <= 255:
                if(len(d)==0):
                    t.join()
                    d.append(track+2)
                    pat2=green
                    pat1=grey
                    pat3=grey
                    pat4=grey
                    pat5=grey
            elif 270 <= center[0] <= 350:
                if(len(d)==0):
                    t.join()
                    d.append(track+3)
                    pat3=green
                    pat2=grey
                    pat1=grey
                    pat4=grey
                    pat5=grey
            elif 365 <= center[0] <= 445:

                if(len(d)==0):
                    t.join()
                    d.append(track+4)
                    pat4=green
                    pat2=grey
                    pat3=grey
                    pat1=grey
                    pat5=grey
            elif 460 <= center[0] <= 540:
                if(len(d)==0):
                    t.join()
                    d.append(track+9)
                    pat5=(0,0,255)
                    pat2=grey
                    pat3=grey
                    pat4=grey
                    pat1=grey


    # Show all the windows
    cv2.imshow("Tracking", frame)
    cv2.imshow("mask",Mask)



	# If the 'q' key is pressed then stop the application
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the camera and all resources
cap.release()
cv2.destroyAllWindows()
