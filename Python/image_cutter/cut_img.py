#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# 
####
# File: cut_img.py
# Project: image_cutter
#-----
# Created Date: Tuesday 11.08.2020, 00:47
# Author: Apop85
#-----
# Last Modified: Tuesday 11.08.2020, 00:47
#-----
# Copyright (c) 2020 Apop85
# This software is published under the MIT license.
# Check http://www.opensource.org/licenses/MIT for further informations
#-----
# Description:
####

import os, threading, re
from PIL import Image, ImageColor
from time import sleep

# Defining in- and output path
image_dir = r".\Input"
target_dir = r".\Output"
# String to extend the filename
filename_extension = "_cropped"
# Default amount of max threads
max_threads = 3
# Setup counters
thread_counter, image_counter = 0, 0
# List of all generated threads
thread_list = []

# Determine the script location
# script_path = os.path.dirname(__file__)
# print(script_path)
# Change path to target subfolder
# input()
# os.chdir(image_dir)

# Save absolut path
abs_image_path = image_dir
abs_target_path = target_dir

help_messages = {
    "thread": "As more threads you generate as faster the script will process all the images. If you have a potato computer keep this number low otherwise it could end in an not responding script or machine."
}

def format_text(text):
    # Cut text to terminal width
    terminal_width=(os.get_terminal_size())[0]
    pattern = re.compile(r'.{3,'+str(terminal_width)+r'}[ \.]')
    return "\n".join(pattern.findall(text))


def init():
    # Ask for max amount of threads
    global max_threads
    valid = False
    while not valid:
        print("Enter max amount of active threads. [1-100] Default = 3 (? for help)")
        answer = input()
        if not answer == "":
            if answer.isdecimal() and 1 <= int(answer) <= 100:
                max_threads = int(answer)
                valid = True
            elif answer == "?":
                print(format_text(help_messages["thread"]))
    process_images()


def process_images():
    global image_dir
    global thread_counter
    global image_counter
    aviable_files = os.listdir(image_dir)
    for filename in aviable_files:
        image_counter += 1
        # Keep idle while max threads reached 
        while thread_counter >= max_threads:
            sleep(0.2)
        # Define and start new thread
        thread_object = threading.Thread(name='ImageProcessor', target=start_process, args=[filename])
        thread_object.start()
        # Save thread in list
        thread_list.append(thread_object)

        thread_counter += 1

    # Wait until all threads are done
    for thread in thread_list:
        thread.join()
    print("Resizing done. Processed {} images".format(image_counter))


def start_process(filename):
    global image_dir
    if filename.endswith(".png"):
        x_start, x_end, y_start, y_end = 10**10,0,10**10,0
        # Open image
        image_object = Image.open(image_dir + "\\" + filename)
        # Get Size of the image
        size_x, size_y = image_object.size
        # Iterate trough each pixel
        for y_pixel in range(0, size_y):
            for x_pixel in range(0, size_x):
                # Read color of pixel
                current_color = image_object.getpixel((x_pixel, y_pixel))
                # Update coordinates if pixel is not empty 
                if current_color != (0,0,0,0):
                    x_start = x_pixel if x_pixel < x_start else x_start
                    x_end = x_pixel if x_pixel > x_end else x_end
                    y_start = y_pixel if y_pixel < y_start else y_start
                    y_end = y_pixel if y_pixel > y_start else y_start
        # Define content area
        crop = (x_start, y_start, x_end, y_end)
        # Start cropping process
        crop_files(filename, crop, image_object)
    

def crop_files(filename, crop_area, image_object):
    global thread_counter
    # Define new image with reduced content
    new_image = image_object.crop(crop_area)
    # Create new filename
    image_name = filename.split(".")
    new_name = ""
    for i in range(0,len(image_name)-1):
        new_name += image_name[i]
    new_name += filename_extension + "." + image_name[-1]
    # Save reduced image
    new_image.save(abs_target_path+"\\"+new_name)

    thread_counter -= 1

    print(filename, "done")


init()
