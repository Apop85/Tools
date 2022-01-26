import os
from shutil import move as moveFile
import re

def findMissing():
    path = r""
    season =  "xyz"
    pattern = re.compile(r".*[Ss]\d\d[FfEe]\d\d.*")
    seasonPattern = re.compile(r".*[Ss](\d\d)[FfEe]\d\d.*")
    episodePattern = re.compile(r".*[Ss]\d\d[FfEe](\d\d).*")
    prefixPattern = re.compile(r"(.*)[Ss]\d\d[FfEe]\d\d.*")

    while not os.path.exists(path):
        path = input("Pfad angeben: ")

    lookupTable = {}
    for currentFolder, subfolders, files in os.walk(path):
        for fileName in files:
            if re.match(pattern, fileName):
                season = int(re.findall(seasonPattern, fileName)[0])
                episode = int(re.findall(episodePattern, fileName)[0])
                prefix = re.findall(prefixPattern, fileName)[0]
                lookupTable.setdefault(season, {})
                lookupTable[season].setdefault(episode, os.path.join(currentFolder, fileName))
                lookupTable[season].setdefault("episodes", [])
                lookupTable[season].setdefault("path", currentFolder)
                lookupTable[season].setdefault("prefix", prefix)
                lookupTable[season]["episodes"] += [episode]
        if season in lookupTable.keys() and "episodes" in lookupTable[season].keys():
            lookupTable[season]["episodes"].sort()

    for season in lookupTable.keys():
        maxEpisodeOfSeason = lookupTable[season]["episodes"][-1]

        for i in range(1, maxEpisodeOfSeason+1):
            if not i in lookupTable[season]["episodes"]:
                missingFilename = lookupTable[season]["prefix"] + f"S{str(season).zfill(2)}E{str(i).zfill(2)} - MISSING.txt"
                path = os.path.join(lookupTable[season]["path"], missingFilename)
                fileWriter = open(path, "w", encoding="utf-8")
                fileWriter.write("")
                fileWriter.close()
                print(f"{missingFilename}")
    print("Done")
        
while True:
    findMissing()