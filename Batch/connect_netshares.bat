@echo off

SETLOCAL ENABLEDELAYEDEXPANSION
set drives="Y: \\PATH\Folder" "Z: \\PATH\Folder"

for %%e in (%drives%) do ( 
    set /A attempt = 1
    REM Auslesen des aktuellen Laufwerks und des Netzwerkpfads
    set currentObject=%%e

    REM Zuschneiden der Variablen
    set driveLetter=!currentObject:~1,2!
    set networkPath=!currentObject:~4,-1!

    :CONNECT
    REM Entfernen des Netzwerkshares falls vorhanden
    if exist !driveLetter! (
        net use !driveLetter! /d /y >NUL
    )

    REM Verbinden des Netzwerkshares
    net use !driveLetter! !networkPath! 8>NUL >NUL 2>NUL

    REM Verbindungsprüfung, schreibe Output gefiltert nach Laufwerksbuchstabe in TMP-Datei
    net use | find "!driveLetter!" >!TMP!\out.tmp
    REM Lese TMP-Datei
    set /p driveStatusFull=<!TMP!\out.tmp
    REM Lösche TMP-Datei
    del !TMP!\out.tmp
    REM Schneide String zu
    set driveStatus=!driveStatusFull:~0,2!

    REM Prüfe Verbindungsstatus
    if "!driveStatus!" NEQ "OK" (
        echo Versuch der Verbindung mit !networkPath! ist fehlgeschlagen!
        set /A attempt+=1
        if !attempt! LEQ 10 (
            echo Starte Versuch #!attempt!
            REM Versuche erneute Verbindung
            goto :CONNECT
        )
    ) else (
        echo !driveStatusFull!
        echo Laufwerk !driveLetter! erfolgreich verbunden!
    )
    set driveStatusFull=""
)


ENDLOCAL