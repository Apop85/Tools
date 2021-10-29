#!/usr/bin/env python3
# -*- coding:utf-8 -*-

####
# File: doubles2.py
# Project: Desktop
#-----
# Created Date: Tuesday 26.10.2021, 21:25
# Author: Apop85
#-----
# Last Modified: Friday 29.10.2021, 13:33
#-----
# Copyright (c) 2021 Apop85
# This software is published under the MIT license.
# Check http://www.opensource.org/licenses/MIT for further informations
#-----
# Description: Experiment, if time can be saved by read out capture- / cdate first 
# Check duplicates by multiple occurencies of the same timestamp
####
import win32com.client
import hashlib, os, re, time
from shutil import copyfile, move

sourceDir=r"\\192.168.1.14\Bilder\Camera"
targetDir=r"C:\Users\rbald\Desktop\Doubles"
# Set the possible filename patterns
datetimePatterns = [
    # *YYYYMMDD_HHMMSS*
    r".*?([1-2][0-9][0-2][0-9][0-1][0-9][0-3][0-9]_[0-2][0-9][0-5][0-9][0-5][0-9]).*?",
    # YYMMDD_HHMMSS*
    r"^([0-2][0-9][0-1][0-9][0-3][0-9]_[0-2][0-9][0-5][0-9][0-5][0-9]).*"
]


filelist = os.listdir(sourceDir)
menge = len(filelist)



def extractDateFromFilename(filename):
    basename = os.path.basename(filename)
    for datetimePattern in datetimePatterns:
        pattern = re.compile(datetimePattern)
        result = re.findall(pattern, basename)
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
            elif matchingIndex == 1:
                # YYMMDD HH:MM:SS
                timestamp = result[0]
                year = timestamp[0:2]
                year = "19" +  year if int(year) > 90 else "20" + year
                month = timestamp[2:4]
                day = timestamp[4:6]
                hour = timestamp[7:9]
                minute = timestamp[9:11]

            return f"{day}.{month}.{year} {hour}:{minute}"
    ctime = os.path.getctime(filename)
    if ctime != None or ctime != "":
        timestamp = time.strftime("%d.%M.%Y %H:%M", time.localtime(ctime))
        return timestamp
    return False
    


def readCaptureDate():
    sh=win32com.client.gencache.EnsureDispatch('Shell.Application',0)
    ns = sh.NameSpace(sourceDir)
    colnum = 0
    columns = []
    aufnahmedatenArray = {}
    
    while True:
        colname=ns.GetDetailsOf(None, colnum)
        if not colname:
            break
        columns.append(colname)
        colnum += 1

    counter = 0
    overallCounter = 0
    for item in ns.Items():
        overallCounter += 1
        # print (item.Path)
        for colnum in range(len(columns)):
            if columns[colnum] == "Aufnahmedatum":
                aufnahmeDatum=ns.GetDetailsOf(item, colnum)
                if aufnahmeDatum == "":
                    aufnahmeDatumNeu = extractDateFromFilename(item.Path)
                    if aufnahmeDatumNeu == False:
                        print("\r" * 100 + "Kein Aufnahmedatum für {} gefunden".format(item.Path))
                        continue
                else:
                    # aufnahmeDatum = aufnahmeDatum.encode("")
                    aufnahmeDatumNeu = aufnahmeDatum.encode('ascii', 'ignore').decode("utf-8")
                    pass
                if aufnahmeDatumNeu == None:
                    print()
                    pass
                aufnahmeDatumNeu = "".join(aufnahmeDatumNeu.split("."))
                aufnahmeDatumNeu = "".join(aufnahmeDatumNeu.split(":"))
                aufnahmeDatumNeu = "".join(aufnahmeDatumNeu.split(" "))
                aufnahmedatenArray.setdefault(aufnahmeDatumNeu, [0, []])
                aufnahmedatenArray[aufnahmeDatumNeu][0] += 1
                aufnahmedatenArray[aufnahmeDatumNeu][1] += [item.Path]
                # print(aufnahmeDatum, aufnahmedatenArray[aufnahmeDatum])

                if len(aufnahmedatenArray[aufnahmeDatumNeu][1]) > 1:
                    counter += 1
            print("\r" * 50 + f"{counter} Identische Aufnahmedaten gefunden  {round(100/menge*overallCounter,2)}%           ", end="")
    
    print(f"\nPrüfung abgeschlossen. Es wurden {counter} identische Aufnahmedaten gefunden")
    return aufnahmedatenArray


def getHashValues(aufnahmedatenArray):
    hashvalues = {}
    doubles = {}
    aufnahmedatenArrayKeys = aufnahmedatenArray.keys()
    counter = 0
    for aufnahmeDatum in aufnahmedatenArray.keys():
        counter += 1
        print("\r" * 50 + f"Prüfe Hash-Werte... {round(100/len(aufnahmedatenArrayKeys)*counter, 2)}%           ", end="")
        if len(aufnahmedatenArray[aufnahmeDatum][1]) > 1:
            for dateiPfad in aufnahmedatenArray[aufnahmeDatum][1]:
                try:
                    with open(dateiPfad,"rb") as f:
                        bytes = f.read() # read entire file as bytes
                        readable_hash = hashlib.md5(bytes).hexdigest();
                    hashvalues.setdefault(readable_hash, [0, []])
                    hashvalues[readable_hash][0] += 1
                    hashvalues[readable_hash][1] += [dateiPfad]

                    if hashvalues[readable_hash][0] >= 2:
                        print(f"Doppelt: {hashvalues[readable_hash][1]}")
                        doubles.setdefault(readable_hash, [0, []])
                        doubles[readable_hash] = hashvalues[readable_hash]
                except:
                    print(f"Datei übersprungen: {dateiPfad}") 
    return doubles

def extractDuplicates(hashvalues):
    for hashvalue in hashvalues.keys():
        if len(hashvalues[hashvalue][1]) > 1:
            dateiCounter = 0
            for filename in hashvalues[hashvalue][1]:
                ursprungspfad = filename
                zielpfad = targetDir + "\\" + os.path.basename(hashvalues[hashvalue][1][counter])
                if dateiCounter == 0:
                    print("Kopiere {} nach {}".format(ursprungspfad, zielpfad))
                    copyfile(ursprungspfad, zielpfad)
                else:
                    print("Verschiebe {} nach {}".format(ursprungspfad, zielpfad))
                    move(ursprungspfad, zielpfad)
                dateiCounter += 1
    print(f"Es wurdern {dateiCounter} Duplikate kopiert/verschoben")

if __name__ == "__main__":
    results = readCaptureDate()
    results = getHashValues(results)
    if len(results.keys()) > 0:
        print("\nBeginne Dateioperationen...")
        extractDuplicates(results)
        print("Aufgabe abgeschlossen")
    else:
        print("\nEs wurden keine Duplikate gefunden")
