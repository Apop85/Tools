#!/usr/bin/env python3
# -*- coding:utf-8 -*-

####
# File: edit_modificationDate.py
# Project: Tools
#-----
# Created Date: Tuesday 26.10.2021, 21:25
# Author: Apop85
#-----
# Last Modified: Friday 29.10.2021, 00:13
#-----
# Copyright (c) 2021 Apop85
# This software is published under the MIT license.
# Check http://www.opensource.org/licenses/MIT for further informations
#-----
# Description: Script to change modification date of files in a directory depending on capture date or filename
####
import win32com.client
import os, re, datetime

# Source directory containing the files to be changed
sourceDir=r"\\192.168.1.14\Bilder\Pilze"
# Localizations of capture date
captureDateNames = ["Aufnahmedatum"]
# Set the possible filename patterns
datetimePatterns = [
    # *YYYYMMDD_HHMMSS*
    r".*?([1-2][0-9][0-2][0-9][0-1][0-9][0-3][0-9]_[0-2][0-9][0-5][0-9][0-5][0-9]).*?",
    # YYMMDD_HHMMSS*
    r"^([0-2][0-9][0-1][0-9][0-3][0-9]_[0-2][0-9][0-5][0-9][0-5][0-9]).*"
]

# Get amount of files
filelist = os.listdir(sourceDir)
menge = len(filelist)

# Get the namespace of the source directory
sh=win32com.client.gencache.EnsureDispatch('Shell.Application',0)
ns = sh.NameSpace(sourceDir)

# Set default values
colnum = 0
columns = []
errorMsg = []
counter = 0



# Get avaiable column names
while True:
    colname=ns.GetDetailsOf(None, colnum)
    if not colname:
        break
    columns.append(colname)
    colnum += 1



# Iterate trough all files
for item in ns.Items():
    counter += 1
    # Get file stats
    fileInfo = os.stat(item.Path)
    # Get modifiy timestamp
    modifiedTimestamp = fileInfo.st_mtime
    # Get creation timestamp
    createdTimestamp = fileInfo.st_ctime
    for colnum in range(len(columns)):
        # Reset error flag
        error=False
        if columns[colnum] in captureDateNames:
            # Read capture date
            aufnahmedatum=ns.GetDetailsOf(item, colnum)
            if aufnahmedatum == "":
                # Get capture date from filename
                filename = os.path.basename(item.Path)
                # Check each pattern
                for datetimePattern in datetimePatterns:
                    pattern = re.compile(datetimePattern)
                    result = re.findall(pattern, filename)
                    if len(result) > 0:
                        # Get index of used pattern
                        matchingIndex = datetimePatterns.index(datetimePattern)
                        if matchingIndex == 0:
                            # YYYYMMDD HH:DD:MM
                            timestamp = result[0]
                            year = timestamp[0:4]
                            month = timestamp[4:6]
                            day = timestamp[6:8]
                            hour = timestamp[9:11]
                            minute = timestamp[11:13]
                            second = timestamp[13:15]
                        elif matchingIndex == 1:
                            # YYMMDD HH:MM:SS
                            timestamp = result[0]
                            year = timestamp[0:2]
                            year = "19" +  year if int(year) > 90 else "20" + year
                            month = timestamp[2:4]
                            day = timestamp[4:6]
                            hour = timestamp[7:9]
                            minute = timestamp[9:11]
                            second = timestamp[11:13]
                        else:
                            # No pattern matched
                            errorMsg += [f"No pattern matched! {filename}"]
                            error=True
            else:
                # Parse capture date
                pattern = re.compile(r".*?(\d\d).*(\d\d).*(\d\d\d\d).*(\d\d).*(\d\d).*$")
                result = re.findall(pattern, aufnahmedatum)
                if len(result) > 0:
                    year = result[0][2]
                    month = result[0][1]
                    day = result[0][0]
                    hour = result[0][3]
                    minute = result[0][4]
                    second = "00"
                else:
                    # Capture date not found
                    errorMsg = [f"Aufnahmedatum konnte nicht ausgelesen werden! {filename}"]
                    error=True
            if not error:
                # Calculate new unix time timestamp
                newTimestamp = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second)).timestamp()
                # Check if change is needed
                if modifiedTimestamp != newTimestamp:
                    print("\r" * 100 + f"Modifiziere Änderungsdatum: Datei {counter} von {menge} - {round(100/menge*counter, 2)}% - " + f"{day}/{month}/{year} {hour}:{minute}:{second}        ", end="")
                    # Change file properties
                    os.utime(item.Path,(0, newTimestamp))
                else:
                    print("\r" * 100 + f"Überspringe Änderungsdatum: Datei {counter} von {menge} - {round(100/menge*counter, 2)}%   " + " " * len(f"{day}/{month}/{year} {hour}:{minute}:{second}       "), end="")

# Print error messages
if len(errorMsg) > 0:
    for message in errorMsg:
        print(message)

print("\nDone")
