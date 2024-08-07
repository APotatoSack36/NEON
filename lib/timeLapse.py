import numpy
import os
from datetime import date
import cv2

def makeTimeLapseVideo(fps, file_location, column, bottom_point, top_point):
    stored_array = []

    image_folder = 'ocean_data\\images'
    video_name = 'video.mp4'

    if column == "temp":
        column = 0
    if column  == "ph":
        column  = 1
    if column == "salt":
        column = 2
    if column  == "sun":
        column  = 3

    ocean_data = numpy.loadtxt(file_location)
    image_number = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    imlength = len(image_number)

    for i in range(0, imlength):
        print(i)
        if ocean_data[i][column] >= bottom_point and ocean_data[i][column] <= top_point:
            numpy.array(stored_array)
            stored_array.append("{}.png".format(int(ocean_data[i][4])))

    print(stored_array)

    if stored_array != []:
        frame = cv2.imread(os.path.join(image_folder, stored_array[0]))
        height, width, layers = frame.shape

        video = cv2.VideoWriter(video_name, 0, fps, (width,height))

        for image in stored_array:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()
    else:
        print("No data points in selected parameters found!")

def image_num():
    image_folder = 'ocean_data\\images'
    image_number = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    imlength = len(image_number)
    return(imlength)