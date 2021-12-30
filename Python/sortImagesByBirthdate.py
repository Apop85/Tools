import os
from shutil import move as moveFile
import datetime
from dateutil import relativedelta
import re

targetDir = r"G:\Bilder\Buddy"

datetimePattern = re.compile(r".*(20\d{2})(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d).*")


birthday = datetime.datetime(
    year=2021,
    month=4,
    day=2
)

fileList = os.listdir(targetDir)

for filename in fileList:
    if re.match(datetimePattern, filename):
        datetimeResults = re.findall(datetimePattern, filename)

        fileTimestamp = datetime.datetime(
            year = int(datetimeResults[0][0]),
            month = int(datetimeResults[0][1]),
            day = int(datetimeResults[0][2]),
            hour= int(datetimeResults[0][3]),
            minute= int(datetimeResults[0][4]),
            second= int(datetimeResults[0][5])
        )
        
        relativeDifference = relativedelta.relativedelta(fileTimestamp, birthday)
        difference = (relativeDifference.years * 12) + relativeDifference.months
        
        folderName = f"Jahr {difference // 12}"
        subfolderName = f"Monat {difference % 12}"

        print(f"{folderName} {subfolderName}")

        yearFolder = os.path.join(targetDir, folderName)
        monthFolder = os.path.join(targetDir, folderName, subfolderName)
        currentFilePath = os.path.join(targetDir, filename)
        targetFilePath = os.path.join(targetDir, folderName, subfolderName, filename)

        if not os.path.exists(yearFolder):
            os.mkdir(yearFolder)
        if not os.path.exists(monthFolder):
            os.mkdir(monthFolder)
        
        moveFile(currentFilePath, targetFilePath)