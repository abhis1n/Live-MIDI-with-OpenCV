# Live MIDI with OpenCV
## Index:
- Introduction
- System Requirements
- Setup Process
- How the program operates
- Understanding the code
## Introduction
Live MIDI is a python script which integrates computer vision with some raw musical talent to create a magic like effect where an artist can play and mix various 
instruments *(drum,synth,bass)* **Live** with a mere swing of his hand. It can be used to send MIDI data to different DAWs and other softwares. The program works fully on python and uses an additional JSON file to store various objects' data.
## System Requirements:
- [rtmidi module](https://pypi.org/project/python-rtmidi/)
- FL studio or any other DAW
- [loopMidi software](https://www.tobias-erichsen.de/software/loopmidi.html)
## Setup Process:
- Install required libraries
  Make sure you have the neccessary libraries installed. You can check the [required files](requirements.txt) for downloading the required libaries.
- Install LoopMidi
  Install a virtual MIDI driver like "loopMIDI" to create a virtual MIDI port. Set up a virtual MIDI port using the loopMIDI software, and make sure it is running.
- Setup loopMIDI device inside FL Studio
  Configure the FL studio, Go to the `options` menu and select `MIDI settings`.
  In the MIDI Settings window, under the `Output` section, make sure that your virtual MIDI port is enabled. If it's not in the list, click on `Refresh device list` or restart FL Studio after creating the virtual port in loopMIDI.
## How the program operates:
The program creates 5X5 virtual tiles on the top and left edges of the live webcam footage screen. 
Trackbars are used to mask and focus down an object (visible to the program through camera),
which have already been configured and stored for several objects.
The user uses the object to touch any of the 10 rectangular regions to initiate or add onto a track.

Now, the tiles on the top and the left serve different purpose. Instruments can be selected by moving the object down the
screen on the left, while tracks for a particular instrument can be changed by howering over the tiles on the top. Threading
is included to allow mixing and adding onto tracks. The program can be terminated by pressing **q**.

## Understanding the code:
The program uses mainly computer vision to create ten rectangles on the screen. The `rtmidi` module is used to send MIDI signals
to the DAW; `cv2` is also used to create trackbars for various parameters which are configurated to mask the object. It finds
contours and encloses the masked object with a yellow circle for the ease of program usage. The program finds if the object
is in a specific rectangular region by using if and else blocks to compare x and y coordinates on the screen and therefore,
sends the appropriate signal based on the same. A deque is used to store various input signals which are popped off after 
adding to the thread. When q is pressed, the application is stopped and consequently, the camera and all other resources
are released.


