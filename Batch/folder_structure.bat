﻿@echo off
@echo off
REM ###
REM  File: folder_structure.bat
REM  Project: Batch
REM -----
REM  Created Date: Thursday 05.03.2020, 20:05
REM  Author: Apop85
REM -----
REM  Last Modified: Thursday 05.03.2020, 21:31
REM -----
REM  Copyright (c) 2020 Apop85
REM  This software is published under the MIT license.
REM  Check http://www.opensource.org/licenses/MIT for further informations
REM -----
REM  Description: Aufgabe 28: Dieses Script legt eine vorgelegte Ordnerstruktur auf einem Laufwerk an
REM  Eventuelle Fehlermeldungen werden dabei unterdrückt.
REM ###

if NOT exist u: (
    goto :bad_ending
)

SETLOCAL ENABLEDELAYEDEXPANSION

REM Definiere zu erstellende Ordner
set folder_layer1="U:\privat" "U:\pst-archive" "U:\zwischenablage"
set folder_layer2="U:\privat\fotogallerie" "U:\privat\musik U:\privat\videos" "U:\pst-archive\2016 U:\pst-archive\2017" "U:\pst-archive\2018" "U:\pst-archive\2019" "U:\pst-archive\2020" "U:\zwischenablage\1_tag" "U:\zwischenablage\2_woche" "U:\zwischenablage\3_monat" "U:\zwischenablage\4_jahr"
set folder_layer3="U:\privat\fotogallerie\ferien" "U:\privat\fotogallerie\freizeit" "U:\privat\musik\mp3" "U:\privat\musik\wav"

REM Iteriere durch alle Arrays
for %%n in (1,2,3) do (
    REM Lese alle Items aus den Arrays aus
    for %%f in (!folder_layer%%n!) do (
        call :random_color
        REM Erstelle Ordner
        md %%f >NUL
        echo Ordner %%f wird erstellt...
    )
)

:good_ending
echo.
echo Ordnerstruktur wurde erstellt
pause
exit

:bad_ending
echo. 
echo Laufwerk U: wurde nicht gefunden
echo Script wird abgebrochen
pause
exit

:random_color
set color_codes=1 2 3 4 5 6 7 8 9 0 a b c d e f
set color_code=
for %%x in (1,2) do ( 
    set /A random_number=!RANDOM!%%16+1
    set /A counter=1
    for %%i in (%color_codes%) do (
        if !counter! equ !random_number! (
            set color_code=!color_code!%%i
        )
        set /A counter=!counter!+1
    )
)
color %color_code%
goto :eof