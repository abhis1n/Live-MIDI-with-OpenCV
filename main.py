import numpy as np
import cv2
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

def setGreen(buttonArr, index, isMute = 0):
    grey = (122,122,122)
    green = (0, 255, 0)
    red = (0, 0, 255)

    for i in range(len(buttonArr)):
        buttonArr[i] = grey

    if isMute:
        buttonArr[index] = red
    else:
        buttonArr[index] = green

def playnote(note=60):
    note_on = [0x90, note, 112] # channel 1, middle C, velocity 112
    note_off = [0x80, note, 0]
    midiout.send_message(note_on)
    time.sleep(0.001)
    midiout.send_message(note_off)

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

grey = (122,122,122)
green = (0, 255, 0)
red = (0, 0, 255)

hasPlayed = False
patColor = [grey] * 5
trkColor = [grey] * 4

# Loading the default webcam of PC.
cap = cv2.VideoCapture(0)
track = 80

# Keep looping
while True:
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
    frame = cv2.rectangle(frame, (80,1), (160,80), patColor[0], -1)
    frame = cv2.rectangle(frame, (175,1), (255,80), patColor[1], -1)
    frame = cv2.rectangle(frame, (270,1), (350,80), patColor[2], -1)
    frame = cv2.rectangle(frame, (365,1), (445,80), patColor[3], -1)
    frame = cv2.rectangle(frame, (460,1), (540,80), patColor[4], -1)

    # Tracks
    frame = cv2.rectangle(frame, (1,80), (80,160), trkColor[0], -1)
    frame = cv2.rectangle(frame, (1,175), (80,255), trkColor[1], -1)
    frame = cv2.rectangle(frame, (1,270), (80,350), trkColor[2], -1)
    frame = cv2.rectangle(frame, (1,365), (80,445), trkColor[3], -1)

    # Button Text
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
                setGreen(trkColor, 0)

            elif 175 <= center[1] <= 255:
                track=70
                setGreen(trkColor, 1)

            elif 270 <= center[1] <= 350:
                track=60
                setGreen(trkColor, 2)

            elif 365 <= center[1] <= 445:
                track=50
                setGreen(trkColor, 3)

        elif center[1] <= 80:
            if 80 <= center[0] <= 160:
                setGreen(patColor, 0)
                if not hasPlayed:
                    hasPlayed = 1
                    playnote(track+1)

            elif 175 <= center[0] <= 255:
                setGreen(patColor, 1)
                if not hasPlayed:
                    hasPlayed = 1
                    playnote(track+2)

            elif 270 <= center[0] <= 350:
                setGreen(patColor, 2)
                if not hasPlayed:
                    hasPlayed = 1
                    playnote(track+3)

            elif 365 <= center[0] <= 445:
                setGreen(patColor, 3)
                if not hasPlayed:
                    hasPlayed = 1
                    playnote(track+4)

            elif 460 <= center[0] <= 540:
                setGreen(patColor, 4, 1)
                if not hasPlayed:
                    hasPlayed = 1
                    playnote(track+9)
        else:
            hasPlayed = 0

    # Show all the windows
    cv2.imshow("Tracking", frame)
    cv2.imshow("mask",Mask)

	# If the 'q' key is pressed then stop the application
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the camera and all resources
cap.release()
cv2.destroyAllWindows()
