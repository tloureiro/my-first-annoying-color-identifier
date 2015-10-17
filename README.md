# my-first-annoying-color-identifier
A simple color identifier for Raspberry Pi.

ReeeeeeeEeeeEeeeeed reeeeeeeeeeeeed blueeeeeeeeeeee white


#### What do you need to run it:
- sudo apt-get install imagemagick fswebcam python-pip sox espeak
- sudo pip install colormath


#### How it works:
1) **fswebcam** takes a picture

2) **imagemagick** divides the picture into 9 frames

3) **imagemagick** reduces each frame's colors to 8

4) from the 8 colors present in a frame, **imagemagick** picks the predominant one

5) **colormath** calculates which of the colors from a subset of 16 colors is the most similar to the main color's rgb values

6) **espeak** speaks the color of the central frame

7) if the color of the central frame is also present in the surrounding frames, **sox** slows down what is being spoken 
