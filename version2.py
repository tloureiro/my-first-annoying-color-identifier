import os
import subprocess
import re


# parse the histogram output provided by imagemagick and return the main color
def getMainColorFromHistogram(output):

    # convert pic.jpg -scale 1x1\! -format '%[pixel:u]' info:-

    maxPixelQty = 0
    maxColor = ""

    for line in output.split("\n"):
        if line.strip() == "": # get rid of strange lines
            continue
        else:
            informationBits = line.strip().split(" ")

            if informationBits[0].split(":")[0].isalnum(): # if the first part is not a number, skip
                score = int(informationBits[0].split(":")[0])
            else:
                continue

            if len(informationBits) > 0 and len(informationBits[len(informationBits) - 1]) > 0: # if last part is empty, skip
                color = informationBits[len(informationBits) - 1]

                if color == "gray(255,255,255)": # this is a bug from imagemagick I think reporting 255,255,255 as gray
                    color = "white"
                elif color == "gray(0,0,0)":
                    color = "black"
                else:
                    color = re.sub("[^a-zA-Z]+", '', color) # remove all numbers and other trash
            else:
                continue

            if score >= maxPixelQty:
                maxPixelQty = score
                maxColor = color

    return maxColor

# initialize the color map (it is going to be used later to reduce the colors present in the picture taken)
os.system("convert xc:white xc:black xc:yellow xc:orange xc:purple  xc:red xc:blue xc:green -append basic_colors_map.png")

for i in range(200):

    # take picture
    os.system("fswebcam -d /dev/video0 --jpeg 100%  -S 2 -F 20 --no-banner pic.jpg")

    # enhance picture's brightness
    os.system("convert pic.jpg -channel rgb -auto-level pic.jpg")

    # divide the picture into 9 quadrants
    os.system("convert pic.jpg -crop 3x3@ quadrant.png")

    quadrantColors = [0 for i in range(9)] # initialize the array with 9 positions

    for i in range(9):

        # reduce the colors of the quadrant
        os.system("convert quadrant-" + str(i) + ".png +dither -colors 16 quadrant-" + str(i) + ".png")

        # now get the main color of this quadrant
        stream = subprocess.check_output(["convert", "quadrant-" + str(i) + ".png", "-scale", "1x1", "-format", "'%[pixel:u]'", "info:-"])
        mainColor = stream.split("\n")[0]

        # produce a pixel image of this color
        os.system("convert xc:" + mainColor + " -append main_color_pixel-" + str(i) + ".png")

        # now map this color to the closest one from our color map
        os.system("convert main_color_pixel-" + str(i) + ".png -remap basic_colors_map.png main_color_remapped-" + str(i) + ".png")

        # get the histogram information of one piece of the whole picture and parse it after
        stream = subprocess.check_output(["convert", "main_color_remapped-" + str(i) + ".png", "-define", "histogram:unique-colors=true", "-format", "%c", "histogram:info:-"])
        quadrantColors[i] = getMainColorFromHistogram(stream)

    # get the middle frame's main color
    middleColor = quadrantColors[len(quadrantColors) / 2]
    colorQuantifier = 0.0

    # now check how many times the color repeats in the frame as the main color
    for color in quadrantColors:
        if color == middleColor:
            colorQuantifier += 1.0/9.0

    print middleColor
    print 1.1 - colorQuantifier

    process = subprocess.Popen(["espeak", middleColor, "--stdout"], stdout=subprocess.PIPE)
    subprocess.Popen(["play", "-t", "wav", "-", "tempo", str(1.1 - colorQuantifier)], stdin=process.stdout)




