import pygame
import sys
import os
import serial
import threading
import json
import time
import cv2
import numpy as np
import subprocess
from ast import literal_eval
from urllib.request import urlopen

import lib.quickScriptPygame as quickScriptPygame
import lib.dumpJsonToDat as dumpJsonToDat
from lib.timeLapse import *

font_size = 35
background_color = (109, 200, 231)
font_color = (5, 28, 45)

screen = quickScriptPygame.screen
pygame.display.set_icon(pygame.image.load("assets\\images\\neon_logo.png"))
pygame.display.set_caption("NEON")
wwidth, wheight = screen.get_size()
scalar = (wheight/1080)

wild_file = dumpJsonToDat.OceanData()
url = r'http://192.168.4.1/capture'
img = None
img_index = 0
program_state = "title"
json_archetype = {'index' : 0, 'temperature': 0, 'ph' : 0, 'salinity': 0, 'light': 0}
time_state = 1

parallax_back = quickScriptPygame.ScrollingImage("assets\\backgrounds\\parallax_back.png", 0, wheight - 346 * scalar * 2, 1201,346, scalar * 2)
parallax_mid = quickScriptPygame.ScrollingImage("assets\\backgrounds\\parallax_mid.png", 0, wheight - 340 * scalar * 1.5, 1200, 340, scalar * 1.5)
parallax_front = quickScriptPygame.ScrollingImage("assets\\backgrounds\\parallax_front.png", 0, wheight - 372 * scalar, 1257, 372, scalar)

live_data_button = quickScriptPygame.Button("assets\\buttons\\title_screen\\live_data{}.png")
settings_button = quickScriptPygame.Button("assets\\buttons\\title_screen\\settings{}.png")
folder_button = quickScriptPygame.Button("assets\\buttons\\title_screen\\folder{}.png")
quit_button = quickScriptPygame.Button("assets\\buttons\\title_screen\\quit{}.png")
live_data_header = quickScriptPygame.Button("assets\\buttons\\headers\\live_data_header{}.png")
settings_header = quickScriptPygame.Button("assets\\buttons\\headers\\settings_header{}.png")

title_logo = quickScriptPygame.Image("assets\\images\\neon_logo_text.png")
footer = quickScriptPygame.Image("assets\\images\\footer.png")

temp_slider = quickScriptPygame.Slider(100, 100, 300, 75, background_color, (237, 26, 82))
ph_slider = quickScriptPygame.Slider(100, 220, 300, 75, background_color, (245, 238, 49))
saline_slider = quickScriptPygame.Slider(100, 340, 300, 75, background_color, (247, 148, 29))
sun_slider = quickScriptPygame.Slider(100, 460, 300, 75, background_color, (57, 181, 74))
timelapse_button = quickScriptPygame.Button("assets\\buttons\\camera\\camera{}.png")

lowerBoundSlider = quickScriptPygame.Slider(100, 460, 300, 75, background_color, (57, 181, 74))
upperBoundSlider = quickScriptPygame.Slider(100, 550, 300, 75, background_color, (57, 181, 74))
plus1 = quickScriptPygame.Button("assets\\buttons\\camera\\operands\\plus{}.png")
minus1 = quickScriptPygame.Button("assets\\buttons\\camera\\operands\\minus{}.png")
plus2 = quickScriptPygame.Button("assets\\buttons\\camera\\operands\\plus{}.png")
minus2 = quickScriptPygame.Button("assets\\buttons\\camera\\operands\\minus{}.png")
finVid = quickScriptPygame.Button("assets\\buttons\\camera\\timelapse\\timelapse{}.png")
text = quickScriptPygame.Text("twcenmt.ttf", font_size, font_color)
image_index = 0

showoff = quickScriptPygame.Image("ocean_data\\images\\{}.png".format(image_index))
frame = quickScriptPygame.Image("assets\\images\\PictureFrame.png")
test_var = 0
womp = True
temp = quickScriptPygame.Image("assets\\images\\temp.png")
pH = quickScriptPygame.Image("assets\\images\\pH.png")
NaCL = quickScriptPygame.Image("assets\\images\\NaCL.png")
sun = quickScriptPygame.Image("assets\\images\\sun.png")

dropDown = quickScriptPygame.Button("assets\\buttons\\dropDown\\dropDown{}.png")

d1 = quickScriptPygame.Button("assets\\buttons\\dropDown\\dropDownDrop{}.png")
d2 = quickScriptPygame.Button("assets\\buttons\\dropDown\\dropDownDrop{}.png")

goal_capture = "ph"
sensor_index = 0

def convert_image_format(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

def changeSensor(snum):
    global sensor_index
    sensor_index = snum

def dropDownWow():
    dropDown.drop_down_open = 1
    d1.create_button(dropDown.x_pos, dropDown.y_pos + dropDown.height, 120, 50, lambda : changeSensor(0))
    text.create_text("Device 0", dropDown.x_pos + 12, dropDown.y_pos + dropDown.height + 35/2)
    d2.create_button(dropDown.x_pos, d1.y_pos + d1.height, 120, 50, lambda : changeSensor(1))
    text.create_text("Device 1", dropDown.x_pos + 12, d1.y_pos + d1.height + 35/2)
    if d1.clicked or d2.clicked:
        dropDown.drop_down_open = False

def initialize():
    global data_timeout, com_port
    config = json.load(open("config.json"))
    data_timeout = config["TIMEOUT"]
    com_port = config["COMPORT"]

def closeProgram():
    global womp
    main_serial.open_state = False
    womp = False
    pygame.quit()
    sys.exit()

def parallaxScroll(layer=(1,1,1), speed=1):
    if layer[0]:
        parallax_back.scale = scalar * 2
        parallax_back.parallax(speed * .5)
    if layer[1]:
        parallax_mid.scale = scalar *1.5
        parallax_mid.parallax(speed * 1)
    if layer[2]:
        parallax_front.scale = scalar
        parallax_front.parallax(speed * 2)

def switchState(ad_stata):
    global program_state 
    program_state = ad_stata

def textOffset(val):
    if abs(val) >=0 and abs(val) < 10:
        return 0
    if abs(val) >=10 and abs(val) < 100:
        return 7
    if abs(val) >= 100 and abs(val) < 1000:
        return 15

class SensorObject:
    def __init__(self):
        self.index = 0
        self.temp = 0
        self.ph = 0
        self.salinity = 0
        self.light = 0
    
    def setValues(self, tup):
        self.index = tup["index"]
        self.temp = tup["temperature"]
        self.ph = tup["ph"]
        self.salinity = tup["salinity"]
        self.light = tup["light"]

OceanData = SensorObject()

class SerialPort:
    global com_port
    def __init__(self):
        try:
            self.com = serial.Serial(com_port, 9600)
            self.open_state = True
        except:
            print("Error connecting to port!")
            self.open_state = False
        self.com_text = json_archetype

    def retryInit(self):
        try:
            self.com = serial.Serial(com_port, 9600)
            self.open_state = True
        except:
            print("Error connecting to port!")
            self.open_state = False
        self.com_text = json_archetype

    def readSerial(self):
        global OceanData
        while self.open_state:
            try:
                self.com_text = self.com.readline()
                self.com_text = self.com_text.decode().strip('\r\n')
                self.com_text = literal_eval(self.com_text)
            except:
                self.open_state = False

def openDataFolder():
    subprocess.Popen(f'explorer "ocean_data\\"') 

def editlowerBoundSlider(change=1):
    lowerBoundSlider.slide_x += 1/3 * change
def editupperBoundSlider(change=1):
    upperBoundSlider.slide_x += 1/3 * change


def cam():
    global img, img_index, womp
    while womp:
        try:
            img_resp = urlopen(url)
            imgnp = np.asarray(bytearray(img_resp.read()), dtype="uint8")
            img = cv2.imdecode(imgnp, -1)
        except:
            break
        if not main_serial.open_state:
            sys.exit()

def saveFrame():
        global img, img_index
        os.chdir("ocean_data\\images")
        cv2.imwrite("{}.png".format(img_index), img)
        img_index += 1
        os.chdir("C:\\Users\\Jcabe\\Desktop\\Code Projects\\Expo2024C")

initialize()

main_serial = SerialPort()
serialThread = threading.Thread(target=main_serial.readSerial)
serialThread.start()

camThread = threading.Thread(target=cam)
camThread.start()
main_program_state  = 1
if __name__ == "__main__":
    wwidth, wheight = screen.get_size()
    scalar = (wheight/1080) * 1.25
    parallax_back.scale = scalar * 2
    parallax_back.resizeParallax()
    parallax_mid.scale = scalar * 1.5
    parallax_mid.resizeParallax()
    parallax_front.scale = scalar
    parallax_front.resizeParallax()

    while main_program_state:
        screen.fill(background_color)
        lastwidth = wwidth
        lastheight = wheight
        wwidth, wheight = screen.get_size()
        scalar = (wheight/1080) * 1.25

        if lastwidth != wwidth:
            parallax_back.resizeParallax()
            parallax_mid.resizeParallax()
            parallax_front.resizeParallax()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_program_state = 0
            if event.type == pygame.VIDEORESIZE:
                width, height = event.size
                if width > 1000:
                    width = 1000
                if height > 1000:
                    height = 1000
                if width < 500:
                    width = 500
                if height < 800:
                    height = 800
                screen = pygame.display.set_mode((width,height), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_1:
                        goal_capture = "temp"
                    case pygame.K_2:
                        goal_capture = "ph"
                    case pygame.K_3:
                        goal_capture = "salt"
                    case pygame.K_4:
                        goal_capture = "sun"

        match program_state:
            case "title":
                parallaxScroll()
                title_logo.draw_image((400,154),((wwidth-400)/2, 100))
                live_data_button.create_button((wwidth - 370)/2, 300, 370, 95, lambda : switchState("live-data"))
                settings_button.create_button((wwidth - 370)/2, 425, 242, 95, lambda : switchState("settings"))
                folder_button.create_button((wwidth - 370)/2 + 275 , 425, 95, 95, lambda : openDataFolder())
                quit_button.create_button((wwidth - 370)/2, 550, 370, 95, lambda : closeProgram())

                footer.draw_image((400, 41), ((wwidth - 400)/2 ,675))

            case "live-data":
                parallaxScroll((1,0,0), .5)
                live_data_header.create_button(0, 0, wwidth, (wwidth/1600) * 158, lambda : switchState("title"))
                timelapse_button.create_button(wwidth - timelapse_button.width, live_data_header.x_pos + live_data_header.height + 5, 65, 50, lambda : switchState("time-lapse"))

                if main_serial.open_state:
                    if main_serial.com_text["index"] == sensor_index:
                        OceanData.setValues(main_serial.com_text)

                    if time_state:
                        init_time = int(time.time())
                        time_state = 0
                    
                    time_check = (int(time.time()) - data_timeout)
                    
                    if time_check == init_time:
                        time_state = 1
                        wild_file.dump_odinfo(main_serial.com_text, img_index)
                        if img is not None:
                            saveFrame()
                        
                    temp_slider.width = wwidth - 200
                    ph_slider.width = wwidth - 200
                    saline_slider.width = wwidth - 200
                    sun_slider.width = wwidth - 200

                    temp.draw_image((31, 75), (temp_slider.x_pos/2 - 31/2, temp_slider.y_pos))
                    pH.draw_image((71,75),(ph_slider.x_pos/2 - 71/2,ph_slider.y_pos))
                    NaCL.draw_image((80,75),(saline_slider.x_pos/2 - 80/2, saline_slider.y_pos))
                    sun.draw_image((75,75),(sun_slider.x_pos/2 - 75/2, sun_slider.y_pos))
                    temp_slider.draw_slider(OceanData.temp, 0, 100)
                    ph_slider.draw_slider(OceanData.ph, 0, 1024)
                    saline_slider.draw_slider(OceanData.salinity, 0, 1024)
                    sun_slider.draw_slider(OceanData.light, 0, 1024)
                    text.create_text("{}".format(OceanData.temp), temp_slider.slide_x - textOffset(OceanData.temp), temp_slider.y_pos - font_size)
                    text.create_text("{}".format(OceanData.ph), ph_slider.slide_x - textOffset(OceanData.ph), ph_slider.y_pos - font_size)
                    text.create_text("{}".format(OceanData.salinity), saline_slider.slide_x - textOffset(OceanData.salinity), saline_slider.y_pos - font_size)
                    text.create_text("{}".format(OceanData.light), sun_slider.slide_x - textOffset(OceanData.light), sun_slider.y_pos - font_size)
                
                    if img is not None:
                        pygame_frame = convert_image_format(img)
                        pygame_surface = pygame.surfarray.make_surface(pygame_frame)
                        pygame_surface = pygame.transform.rotate(pygame_surface, -90)
                        pygame_surface = pygame.transform.flip(pygame_surface, flip_x=1, flip_y=0)
                        screen.blit(pygame_surface, (160, 550))

                elif not serialThread.is_alive():
                    main_serial.retryInit()
                    serialThread = threading.Thread(target=main_serial.readSerial)
                    serialThread.start()
                if not camThread.is_alive():
                    camThread = threading.Thread(target=cam)
                    camThread.start()
                dropDown.create_button(30, 550, 120, 50, lambda: dropDownWow())
                if dropDown.drop_down_open == True:
                    dropDownWow()

            case "settings":
                parallaxScroll((1,0,0))
                settings_header.create_button(0, 0, wwidth, (wwidth/1600) * 158, lambda : switchState("title"))
                text.create_text("{}".format(com_port), 0, 90)
                text.create_text("{}".format(data_timeout), 0, 120)

            case "time-lapse":
                live_data_header.create_button(0, 0, wwidth, (wwidth/1600) * 158, lambda : switchState("live-data"))
                parallaxScroll((1,0,0), .5)
                lowerBoundSlider.drawAdjustableSlider(0, 1000)
                text.create_text("Low.: {}".format(lowerBoundSlider.scaled_var), 5, 460 + 75/4)
                upperBoundSlider.drawAdjustableSlider(0, 1000)
                text.create_text("Upp.: {}".format(upperBoundSlider.scaled_var), 5, 550 + 75/4)
                text.create_text("Current Filter: {}".format(goal_capture), 90, 150-35)

                showoff.timelapse_img(image_index, (320, 240), (90, 150))
                frame.draw_image((323, 243), (88, 148))
                if time_state:
                    init_time = int(time.time())
                    time_state = 0
                
                time_check = (int(time.time()) - .1)
                
                if time_check >= init_time:
                    time_state = 1
                    image_index += 1
                    if image_index >= image_num():
                        image_index = 0
                        
                plus1.create_button(415, 460 + 75/4, 40, 40, lambda : editlowerBoundSlider(1))
                minus1.create_button(455, 460+75/4, 40, 40, lambda : editlowerBoundSlider(-1))
                plus2.create_button(415, 550+75/4, 40, 40, lambda : editupperBoundSlider(1))
                minus2.create_button(455, 550+75/4, 40, 40, lambda : editupperBoundSlider(-1))
                finVid.create_button(50, 650, 400, 100, lambda : makeTimeLapseVideo(10, "ocean_data\\biweek_2024-04-03 0.dat", goal_capture, lowerBoundSlider.scaled_var, upperBoundSlider.scaled_var))
        
        pygame.display.update()
    closeProgram()