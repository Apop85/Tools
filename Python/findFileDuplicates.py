#!/usr/bin/env python3
# -*- coding:utf-8 -*-

####
# File: findFileDuplicates.py
# Project: Tools
#-----
# Created Date: Tuesday 26.10.2021, 20:23
# Author: Apop85
#-----
# Last Modified: Friday 29.10.2021, 12:04
#-----
# Copyright (c) 2021 Apop85
# This software is published under the MIT license.
# Check http://www.opensource.org/licenses/MIT for further informations
#-----
# Description: Check folder for duplicate files by hash value. 
# Keep one file and move duplicates into a specified directory
####


import hashlib, os
from shutil import copyfile, move

# Define used directories
# Source directory containing the files to be checked
sourceDir=r"\\192.168.1.14\Bilder\Pilze"
# Target directory where duplicate files get copied/moved
targetDir=r"C:\Doppelt"


# Create folder if not exists
if not os.path.exists(targetDir):
    os.mkdir(targetDir)

# Get amount of files
filelist = os.listdir(sourceDir)
menge = len(filelist)

# Set default values
counter = 1
hashtable = {}
totalDoubles = 0

# Check each file
for filename in filelist:
    print("\r" * 50 + f"Lese Foto {counter} von {menge}" + f"  {round(100/menge*counter, 2)}%         ", end="")
    counter += 1
    try:
        # Get hashvalue of file
        with open(sourceDir + "\\" + filename,"rb") as f:
            bytes = f.read() # read entire file as bytes
            readable_hash = hashlib.md5(bytes).hexdigest()
            
            # Save hash value, amount and filenames
            hashtable.setdefault(readable_hash, [0, []])
            hashtable[readable_hash][0] += 1
            hashtable[readable_hash][1] += [filename]

            # Check if more than two files got the same hash value
            if hashtable[readable_hash][0] >= 2:
                totalDoubles += 1
                # Ensure the file with the least amount of characters (if same file name) is choosen
                hashtable[readable_hash][1].sort(reverse=True)
                print("\r" * 50 + f"{totalDoubles} Doppelt: {hashtable[readable_hash][1]}                ") 
    except:
        print("\r" * 50 + f"Datei übersprungen: {filename}")
 
# Iterate trough hash values
for hashvalue in hashtable.keys():
    # Check if more than one file was found with this hash value
    if len(hashtable[hashvalue][1]) > 1:
        # Ensure the file with the least amount of characters (if same file name) is choosen
        hashtable[hashvalue][1].sort(reverse=True)
        # Reset counter
        counter = 0
        for filename in hashtable[hashvalue][1]:
            # Define source and target file path
            source = sourceDir + "\\" + hashtable[hashvalue][1][counter]
            target = targetDir + "\\" + hashtable[hashvalue][1][counter]
            if counter == 0:
                # Copy first file
                print("Kopiere {} nach {}".format(filename, target))
                copyfile(source, target)
            else:
                # Move all other files
                print("Verschiebe {} nach {}".format(filename, target))
                move(source, target)
            counter += 1
