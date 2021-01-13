#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# 
####
# File: transformText.py
# Project: Texttranformation
#-----
# Created Date: Wednesday 16.12.2020, 14:59
# Author: Apop85
#-----
# Last Modified: Wednesday 16.12.2020, 15:45
#-----
# Copyright (c) 2020 Apop85
# This software is published under the MIT license.
# Check http://www.opensource.org/licenses/MIT for further informations
#-----
# Description:
#  Transforms text into similar symbols
####

# Modulimport
from pyperclip import copy, paste
from time import sleep
from random import choice as randomChoice

# Umwandlungstabelle
transformations = {"a": ["α", "ѧ"], "b": [], "c": ["Ϛ"], "d": [], "e": ["ε", "ϵ", "℮"], "f": ["ϝ", "ƒ"], "g": [], "h": ["η"], "i": ["ι"], "j": ["ɹ"], "k": ["κ", "ᴋ"], "l": [], "m": ["ϻ"], "n": ["π", "ƞ", "ϰ", "ռ"], "o": ["ο", "σ", "ᴑ"], "p": ["φ", "ϸ"], "q": ["ϙ"], "r": [], "s": [], "t": ["τ", "ͳ", "Ե", "Է"], "u": ["μ", "υ", "ʊ"], "v": ["ν"], "w": ["ω", "ш"], "x": ["χ"], "y": ["ψ", "ʏ"], "z": ["ƶ", "ᴢ"],
                    "A": ["Ѧ", "λ", "Λ"], "B": ["β", "ß"], "C": [], "D": [], "E": ["ξ", "Σ"], "F": ["Ϝ", "Ƒ"], "G": ["Ɠ"], "H": [], "I": [], "J": ["ɺ"], "K": [], "L": [], "M": ["Ϻ"], "N": ["Π", "Ɲ", "Ո"], "O": ["Φ", "Ω"], "P": ["Ϸ"], "Q": ["Ϙ"], "R": ["Ʀ"], "S": ["Տ"], "T": ["Τ", "Ͳ"], "U": ["Ʊ", "Ʋ"], "V": [], "W": ["Ɯ"], "X": ["Χ"], "Y": ["Υ", "Ψ", "Ⴤ"], "Z": ["Ƶ"]}

def menu():
    # Ausgabe Hauptmenü
    print("Quelle des Textes auswählen")
    # Auswahlmöglichkeiten
    choices = [ "Von Zwischenablage (einmalig)", "Von Zwischenablage (durchgehend)", "Von Eingabe", "Exit"]
    # Gebe Auswahl zurück
    return printMenu(choices)


def printMenu(choices):
    # Ausgabe des Menüs und Validierung der Eingabe
    while True:
        counter = 1
        print("#######################")
        # Gebe jedes Item des Menüs aus
        for item in choices:
            print(str(counter) + ". " + item)
            counter += 1
        print("#######################")
        choice = input("Auswahl: ")

        # Prüfe ob Eingabe eine Zahl und diese innerhalb der Auswahlmöglichkeiten liegt
        if choice.isdecimal() and int(choice) > 0 and int(choice) <= len(choices):
            # Gebe Auswahl zurück
            return choice
        else:
            # Gebe Fehlermeldung aus
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("Auswahl ungültig. Gültige Auswahl: 1 bis {}".format(len(choices)))
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


def singleTransformation():
    # Lese Zwischenablage aus
    print("Warte auf Text aus Zwischenablage. Bitte jetzt kopieren...")
    # Kopiere Defaultwert
    copy("0")
    while paste() == "0":
        sleep(0.5)
    # Kopiere transformierten Text in die Zwischenablage
    copy(transformText(paste()))
    print("Umgewandelter Text befindet sich in der Zwischenablage!")


def transformText(text):
    new_text = ""
    # Prüfe jeden Buchstaben
    for letter in text:
        # Prüfe ob Buchstabe in Umwandlungstabelle vorhanden ist
        if letter in transformations.keys() and len(transformations[letter]) > 0:
            # Wähle eineen zufälliges Zeichen für den Buchstabem aus der Umwandlungstabelle
            new_text += randomChoice(transformations[letter])
        else:
            # Ist kein Zeichen für den Buchstaben vorhanden, lasse diesen stehen. 
            new_text += letter
    return new_text
    

def multipleTransformations():
    # Ruft die Abfrage unendlich oft auf und warted dazwischen jeweils 10 sekunden. 
    # So kann text normal geschrieben, ausgeschnitten und transformiert eingefügt werden
    while True:
        singleTransformation()
        sleep(10)

def textTransformation():
    # Manuelle Eingabe des umzuwandelnden Textes
    text_to_transform = input("Text zum Umwandlen eingeben: ")
    transformed_text = transformText(text_to_transform)
    print("Transformierter Text:\n {}".format(transformed_text))
    input("Enter zum fortfahren")
    print()

def mainLoop():
    # Hauptloop zur Steuerung der Programmabfolge
    while True:
        choice = menu()
        if choice == "1":
            # Rufe einzelntranformation aus Zwischenablage aus
            singleTransformation()
        elif choice == "2":
            # Rufe mehrfachtransformation aus Zwischenablage aus
            multipleTransformations()
        elif choice == "3":
            # Rufe einzeltranformation aus manueller Eingabe auf
            textTransformation()
        elif choice == "4":
            # Beende den Loop und somit das Programm
            break

mainLoop()