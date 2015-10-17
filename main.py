import os
import subprocess
import re
import sys
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

def getClosestColorNameByRGB(red, green, blue, colorDictionary):

    minDistance = sys.maxint
    closestColor = ''
    color = sRGBColor(red, green, blue)
    lab1 = convert_color(color, LabColor)

    for colorName in colorDictionary:

        dictionaryColor = sRGBColor(colorDictionary[colorName][0], colorDictionary[colorName][1], colorDictionary[colorName][2])
        lab2 = convert_color(dictionaryColor, LabColor)
        distance = delta_e_cie2000(lab1, lab2)
        if distance < minDistance:
            minDistance = distance
            closestColor = colorName

    print minDistance
    return closestColor


colorDictionary = {
    'black': (0, 0, 0),
    'gray': (128, 128, 128),
    'silver': (192, 192, 192),
    'white': (255, 255, 255),
    'maroon': (128, 0, 0),
    'red': (255, 0, 0),
    'olive': (128, 128, 0),
    'yellow': (255, 255, 0),
    'green': (0, 128, 0),
    'lime': (0, 255, 0),
    'teal': (0, 128, 128),
    'aqua': (0, 255, 255),
    'navy': (0, 0, 128),
    'blue': (0, 0, 255),
    'purple': (128, 0, 128),
    'fuchsia': (255, 0, 255)
}

for i in range(200):

    # take picture
    os.system("fswebcam -d /dev/video0 --jpeg 85%  -S 3 -F 10 --no-banner -r 300x300 pic.jpg")

    # enhance picture's brightness
    os.system("convert pic.jpg -channel rgb -auto-level pic.jpg")

    # divide the picture into 9 quadrants
    os.system("convert pic.jpg -crop 3x3@ quadrant.png")

    quadrantColors = [0 for i in range(9)] # initialize the array with 9 positions

    for i in range(9):

        # reduce the colors of the quadrant
        os.system("convert quadrant-" + str(i) + ".png +dither -colors 8 quadrant-" + str(i) + ".png")

        # now get the main color of this quadrant
        stream = subprocess.check_output(["convert", "quadrant-" + str(i) + ".png", "-format", "%c", "histogram:info:-"])
        mainColor = stream.split("\n")[0]

        red = int(mainColor.split("(")[-1].split(")")[0].split(",")[0])
        green = int(mainColor.split("(")[-1].split(")")[0].split(",")[1])
        blue = int(mainColor.split("(")[-1].split(")")[0].split(",")[2])

        quadrantColors[i] = getClosestColorNameByRGB(red, green, blue, colorDictionary)

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