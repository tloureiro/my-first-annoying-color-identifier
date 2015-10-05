import os
import subprocess


# parse the histogram output provided by imagemagick and return the main color
def getMainColorFromHistogram(output):

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
                continue

            if score >= maxPixelQty:
                maxPixelQty = score
                maxColor = color

    return maxColor

# initialize the color map (it is going to be used later to reduce the colors present in the picture taken)
os.system("convert xc:white xc:black xc:green xc:red xc:blue xc:yellow xc:violet xc:pink xc:brown xc:orange -append basic_colors_map.png")

for i in range(200):

    # take picture
    os.system("fswebcam -d /dev/video0 --jpeg 100%  -S 2 -F 10 --no-banner pic.jpg")

    # enhance picture's brightness
    os.system("convert pic.jpg -channel rgb -auto-level pic.jpg")

    # reduce the colors of the picture using the color map
    os.system("convert pic.jpg -remap basic_colors_map.png reduced_colors_pic.png")

    # divide the picture into 9 quadrants
    os.system("convert reduced_colors_pic.png -crop 3x3@ quadrant.png")

    quadrantColors = [0 for i in range(9)] # initialize the array with 9 positions

    for i in range(9):
        # get the histogram information of one piece of the whole picture and parse it after
        stream = subprocess.check_output(["convert", "quadrant-" + str(i) + ".png", "-define", "histogram:unique-colors=true", "-format", "%c", "histogram:info:-"])
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




