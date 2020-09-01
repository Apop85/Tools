#!/usr/bin/env python3
# -*- coding:utf-8 -*-

####
# File: walk_the_folders.py
# Project: sonstige_uebungen
#-----
# Created Date: Monday 20.04.2020, 12:17
# Author: Apop85
#-----
# Last Modified: Tuesday 21.04.2020, 23:00
#-----
# Copyright (c) 2020 Raffael Baldinger
# This software is published under the MIT license.
# Check http://www.opensource.org/licenses/MIT for further informations
#-----
# Description: This script analyzes every Folder and Subfolder and lists Folder, Subfolder and Files as well as filesize for each extension.
# Difference to v1: It analyzes folders on the fly. No need for preprocessing
####
import os, re

def print_n_save(content):
    print(content)
    # öffne Datei
    file_writer = open(target_file, "a", encoding="utf-8")
    # Schreibe in Datei
    file_writer.write(content + "\n")
    # Speichere Output-Datei
    file_writer.close()

def choose_size_format(byte_amount):
    format_table = { "b" : 1, "kb" : 1000, "mb" : 1000000, "gb" : 1000000000}
    for key in format_table.keys():
        if len(str(int(byte_amount/format_table[key]))) < 4 or key == "gb":
            if key != "b":
                value = byte_amount/format_table[key]
                value = "%.2f" % value
                return str(value) + " " + key
            else:
                return str(int(byte_amount/format_table[key])) + " " + key

# Fordere Zielpfad an
while True:
    target_dir = input("Bitte Zielpfad angeben: ")
    # Prüfe ob Pfad ein Ordner ist und existiert
    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        break
    else:
        print("Pfad konnte nicht gefunden werden")

# Fordere Pfad für die Zieldatei an
while True:
    target_file = input("Bitte Pfad für Ausgabedatei angeben: ")
    # Splitte Pfad auf
    rel_path = target_file.split("\\")
    del rel_path[-1]
    # Füge absoluter Pfad zusammen
    rel_path = "\\".join(rel_path)
    if os.path.exists(rel_path) and not os.path.isdir(target_file):
        break
    elif os.path.isdir(target_file):
        print(target_file + " ist keine Datei. Beispiel: C:\\output.txt")
    else:
        print("Pfad " + rel_path + " konnte nicht gefunden werden.")

# Frage ob nach jedem Eintrag eine Pause eingelegt werden soll
pause = "na"
while not pause in ["0","1"]:
    pause = input("Nach jedem Ordner eine Pause? (0 = nein, 1 = ja): ")


# Füllelemente
filler = "█"
filler2 = "░"
# Leere Resultattabelle erstellen
result_table = {target_dir : {}}

# Erstelle Walk-Generator
folder_table = os.walk(target_dir)

# Muster zur erkennung von Dateiendungen
file_pattern = re.compile(".*\..{2,5}")

# Prüfe alle Einträge
for folder, subfolders, filenames in folder_table:
    extension_sizes = {}
    print_n_save(filler*100)
    print_n_save(folder.center(100))
    print_n_save(filler2*100)
    print_n_save(" UNTERORDNER ".center(100, filler2))
    subfolder_count = 0
    for subfolder in subfolders:
        subfolder_count += 1
        print_n_save(str(subfolder_count) + ". " + subfolder)
    print_n_save((" TOTAL UNTERORDNER: " + str(subfolder_count) + " ").center(100, filler2))
    print_n_save(filler2*100)
    print_n_save(filler2*100)
    print_n_save(" FILES ".center(100, filler2))
    filename_count = 0
    for filename in filenames:
        filename_count += 1
        print_n_save(str(filename_count) + ". " + filename)
        if file_pattern.match(filename):
            extension = filename.split(".")[-1]
        else:
            extension = "none"
        extension_sizes.setdefault(extension.lower(), 0)
        file_size = (os.stat(folder + "\\" + filename)).st_size
        extension_sizes[extension.lower()] += file_size
    print_n_save((" TOTAL FILES: " + str(filename_count) + " ").center(100, filler2))
    print_n_save(filler2*100)
    print_n_save(filler2*100)
    print_n_save(" DATEIENDUNGEN ".center(100, filler2))
    for key in extension_sizes.keys():
        print_n_save(key.ljust(10) + choose_size_format(extension_sizes[key]))
    print_n_save(filler2*100)
    if pause == "1":
        input("Enter zum fortfahren...")    



