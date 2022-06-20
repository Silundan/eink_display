#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import signal
import RPi.GPIO as GPIO
import gc
import os
import time
import glob
import json
import random
import asyncio
import datetime
import configparser
from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne
from inky.auto import auto
from inky.inky_uc8159 import CLEAN

# Loading from config
conf = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(';')]})
conf.read('/home/pi/eink_display/weather/config.ini')

project_folder = conf['WEATHER']['project_folder']
img_path = project_folder + "img/"
weather_path = project_folder + "weather/"
weather_data = weather_path + "data/"
weather_icon = weather_path + "icons/"

gc.enable()
pick_mod = "D"
label = ""
last_pic = ""
saturation = 0.5 # between 0 an 1

# Gpio pins for each button (from top to bottom)
BUTTONS = [5, 6, 16, 24]

# These correspond to buttons A, B, C and D respectively
LABELS = ['A', 'B', 'C', 'D']

ICON = {
"01d":"B",
"01n":"C",
"02d":"H",
"02n":"I",
"03d":"N",
"03n":"N",
"04d":"Y",
"04n":"Y",
"09d":"Q",
"09n":"Q",
"10d":"R",
"10n":"R",
"11d":"O",
"11n":"O",
"13d":"W",
"13n":"W",
"50d":"J",
"50n":"K",
"base":")",
"unknown":")"
}

# Set up RPi.GPIO with the "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)

# Buttons connect to ground when pressed, so we should set them up
# with a "PULL UP", which weakly pulls the input signal to 3.3V.
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    global label, pick_mod
    label = LABELS[BUTTONS.index(pin)]
    print("Button press detected on pin: {} label: {}".format(pin, label))

    if label == "A":
        pick_mod = label
        button_A("button")

    elif label == "B":
        pick_mod = label
        button_B("button")

    elif label == "C":
        pick_mod = label
        button_C("button")

    elif label == "D":
        pick_mod = label
        button_D("button")

    gct = time.time()
    gc.collect()
    gctime = (time.time() - gct)
    print(f"Garbage collection took {gctime} seconds.")

def time_convert(UNIXtime):
    local_time = time.gmtime(UNIXtime)
    local_time = time.strftime('%H:%M:%S', local_time)
    return local_time

def loop_action(pick_mod):
    t = 0
    if pick_mod == "A":
        t = button_A("loop")
    elif pick_mod == "B":
        t = button_B("loop")
    elif pick_mod == "C":
        t = button_C("loop")
    elif pick_mod == "D":
        t = button_D("loop")
    return t

async def foo(msg):
    global pick_mod
    last_quarter = 0
    while 1:
        start = time.time()
        t = 0
        if pick_mod == "A":
            n = 15
        else:
            n = 5 # interval (in min) for loop cycle, default 15 for A, 5 for others
        print("This is the start of another", msg)
        quarter = datetime.datetime.now().minute

        if (quarter % n == 0):
            t = loop_action(pick_mod)
        elif ((quarter-1) % n == 0) and (quarter-last_quarter == 2):
            t = loop_action(pick_mod)
        else:
            pass

        last_quarter = quarter
        gct = time.time()
        gc.collect()
        gctime = (time.time() - gct)
        print(f"Garbage collection took {gctime} seconds.")
        await asyncio.sleep(60-t-gctime)
        print("This loop cycle ended", str(time.time()-start))

def button_A(where):
    global weather_icon
    start = time.time()
    print("Button A event, from", where)

    #reading the json files in the folder (presumbly the weather jsons gathered from get_weather.py)
    weather_file_path = weather_data + "*.json"
    cities = glob.glob(weather_file_path)
    #number assigned for each json, so it will be presented in the order which user put in config.ini
    if len(cities) == 0:
        pass
    else:
        cities.sort()
        # print(cities)
        
        #creating a blank list to hold the gathered weather data
        cities_weather = []
        last_mod = ""
        oc = ""
        out_city = []
        out_txt = []
        #loading the data from json, adding them to the list in exact order, per city basis
        for i in range(len(cities)):
            with open(cities[i], "r") as fin:
                data = json.load(fin)
                if i != 0:
                    pass
                else:
                    lastmod = os.path.getmtime(cities[i])
                    lastmod = time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(lastmod))
                    last_mod = "Last Update : " + lastmod

                cities_weather.append(data)
                timezone = cities_weather[i]['timezone']
                oc = f"{cities_weather[i]['name']}\nGMT {['', '+'][timezone>0]}{(timezone/3600)}\n{cities_weather[i]['weather'][0]['icon']}"
                out_city.append(oc)

                p = (f"Temp  {cities_weather[i]['main']['temp']:.1f} ({cities_weather[i]['main']['temp_min']:.1f} ~ {cities_weather[i]['main']['temp_max']:.1f})\n")
                p += (f"Feels {cities_weather[i]['main']['feels_like']:.1f}  Humidity {cities_weather[i]['main']['humidity']}%\n")
                p += (f"Sunrise {time_convert(cities_weather[i]['sys']['sunrise']+timezone)}\nSunset {time_convert(cities_weather[i]['sys']['sunset']+timezone)}\n")

                out_txt.append(p)

        w = inky.WIDTH
        h = inky.HEIGHT

        img = Image.new("P", (w, h), inky.WHITE)
        header_font = ImageFont.truetype(FredokaOne, 40)
        font = ImageFont.truetype(FredokaOne, 26)
        icon_font = ImageFont.truetype(project_folder+"meteocons.ttf", 60)
        draw = ImageDraw.Draw(img)

        # width, height = font.getsize(out)  # Width and height of quote
        w_h = h - font.getsize("ABCD ")[1] # ____.getsize() : [0] for width, [1] for height
        h3 = w_h / 3
        w_hh = header_font.getsize("ABCD ")[1] #get header font height
        w_hhh = font.getsize("ABCD ")[1]

        draw.line((5, h3, w-5, h3), fill=inky.BLUE, width=2)
        draw.line((5, h3*2, w-5, h3*2), fill=inky.GREEN, width=2)
        draw.line((5, w_h, w-5, w_h), fill=inky.RED, width=2)

        # get the max width of all city names, to align the details on the right later
        c = 0
        for i in range(3):
            city_name = out_city[i].split("\n")
            d = header_font.getsize(city_name[0])[0]
            if d > c:
                c = d

        disp_col = [inky.BLUE, inky.GREEN, inky.RED]
        # drawing the texts in their rectangle
        for i in range(3):
            details = out_city[i].split("\n")
            if i == 0:
                y = 0
            elif i == 1:
                y = h3
            elif i == 2:
                y = h3 * 2
            
            draw.text((5,y), details[0], disp_col[i], header_font) # City name
            draw.text((5,y+w_hh), details[1], disp_col[i], font) # timezone in GMT
            val_y = y+w_hh+w_hhh
            draw.text((5, int(val_y)), ICON[details[2]], disp_col[i], icon_font)
            draw.text((c + 20, (y + 10)), out_txt[i], fill=disp_col[i], font=font, align="left") # details on the right (temp, feels like, etc.)
            draw.text((5,w_h), last_mod, inky.BLACK, font)

    inky.set_image(img)
    inky.show()

    t = time.time()-start
    print(f"Weather function ended, used "+str(t)+" seconds.")
    return t

def button_B(where):
    start = time.time()
    print("Button B event, from", where)

    t = time.time()-start
    print(f"Button B function ended, used "+str(t)+" seconds.")
    return t


def button_C(where):
    start = time.time()
    print("Button C event, from", where)

    inky = auto(ask_user=True, verbose=True)

    for _ in range(2):
        for y in range(inky.height - 1):
            for x in range(inky.width - 1):
                inky.set_pixel(x, y, CLEAN)

        inky.show()
        time.sleep(1.0)

    t = time.time()-start
    print(f"Clear function ended, used "+str(t)+" seconds.")
    return t



def button_D(where):
    global last_pic, saturation
    start = time.time()
    print("Button D event, from", where)

    img_list = glob.glob(img_path + '*.jpg')
    if len(img_list) == 0:
        pass
    else:
        img_list.sort()

        new_pic = random.choice(img_list)
        while new_pic == last_pic:
            new_pic = random.choice(img_list)
        last_pic = new_pic
        print(new_pic)

        with open(new_pic, "rb") as fin:
            image = Image.open(fin)
            resizedimage = image.resize(inky.resolution)

            inky.set_image(resizedimage, saturation=saturation)
            inky.show()
            image.close()

    t = time.time()-start
    print(f"Image function ended, used "+str(t)+" seconds.")
    return t

inky = auto(ask_user=True, verbose=True)
inky.set_border(inky.BLACK)
button_D("start") #init screen, default button D (random picture display)
gc.collect()
print("beepboop")
# Loop through out buttons and attach the "handle_button" function to each
# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
# picking a generous bouncetime of 250ms to smooth out button presses.
for pin in BUTTONS:
    GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=250)

loop = asyncio.run(foo("loop"))
# Finally, since button handlers don't require a "while True" loop,
# we pause the script to prevent it exiting immediately.
signal.pause()
print("SOMETHING AFTER SIGNAL PAUSE")
