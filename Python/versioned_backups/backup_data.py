#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# 
####
# File: backup_data.py
# Project: Scripts
#-----
# Created Date: Friday 19.02.2021, 13:13
# Author: Apop85
#-----
# Last Modified: Friday 19.02.2021, 17:53
#-----
# Copyright (c) 2021 Apop85
# This software is published under the MIT license.
# Check http://www.opensource.org/licenses/MIT for further informations
#-----
# Description: Script to create a versioned history of files in a given directoy
# 
# Open Script with <pathToScript> <pathToSource> <pathToBackupDir>
####

#   _____       _ _   _       _ _          _   _             
#  |_   _|     (_) | (_)     | (_)        | | (_)            
#    | |  _ __  _| |_ _  __ _| |_ ______ _| |_ _  ___  _ __  
#    | | | '_ \| | __| |/ _` | | |_  / _` | __| |/ _ \| '_ \ 
#   _| |_| | | | | |_| | (_| | | |/ / (_| | |_| | (_) | | | |
#  |_____|_| |_|_|\__|_|\__,_|_|_/___\__,_|\__|_|\___/|_| |_|

# Print title
print("█" * 80)
print("█" + "Backup job".center(78) + "█")
print("█" * 80)


# Import operating system module
import os
# Import argv-object from system module to enable passing arguments to the script
from sys import argv
# Import pickle module to export and import data
import pickle
# Import shutil module to copy files
from shutil import copy
# Import sha512 object from hashlib module to get hashvalues of files
from hashlib import sha512
# Import subprocess module to execute and catch cmd commands
import subprocess
# Import datetime module to convert unixtime to date
from datetime import datetime

# Change working directory to script directory
script_path = os.path.dirname(__file__)

# Define core variables
source_dir = argv[1]
backup_dir = argv[2]
# source_dir = r"D:\Schuldokumente\Kursjahr 2\IPA\IPA-Dokumente"
# backup_dir = r"Z:\Backups\IPA"
backup_log = os.path.join(backup_dir, "backup.log")
script_data_folder = os.path.join(script_path, "scriptData")
script_data_file = os.path.join(script_data_folder, "backupData.pickle")
serial_folder_prefix = "Tag "
today = datetime.now().strftime("%d.%m.%Y")
version_delimiter = "="



#   ______                _   _                 
#  |  ____|              | | (_)                
#  | |__ _   _ _ __   ___| |_ _  ___  _ __  ___ 
#  |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
#  | |  | |_| | | | | (__| |_| | (_) | | | \__ \
#  |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/

def createFolder(path):
    # Create folder
    os.mkdir(path)
    # Check if folder was created
    if not os.path.exists(path):
        raise Exception(f"Failed to create Folder {path}")

def getSourceFileInformations(file_list, script_data_files):
    print("Collect source file data...", end="")
    # Load filehashes if exists
    if os.path.exists(script_data_file):
        file_reader = open(script_data_files, "rb")
        file_informations = {
            "source" : {},
            "backups" : pickle.load(file_reader)
        }
        file_reader.close()
    else:
        # Create default file_informations dictionary
        file_informations = {
            "source" : {}, 
            "backups" : {}
        }

    need_to_backup = False
    # Build source information list
    for filename in file_list:
        # Get hash value if file is not in source dictionary keys
        if not filename in file_informations["source"].keys():
            archived_flag = False
            # Get file attributes
            file_attributes = subprocess.run(["attrib", filename], stdout=subprocess.PIPE)
            file_attributes = (file_attributes.stdout).decode("utf-8")
            file_attributes = file_attributes.split(" ")[0]
            # Check if file is archived already
            if "A" in file_attributes:
                archived_flag = True
            else:
                need_to_backup = True

            # Add file path, hash of file and "A" attribute to dictionary
            file_informations["source"].setdefault(filename, 
                {
                    "archived": archived_flag
                }
            )
    print("Done")
    return file_informations, need_to_backup


def getFileHash(filename):
    print(f"Get hash value of {os.path.basename(filename)}...", end="")
    # Define hash type
    file_hash = sha512()
    # Define blocksize to pass in hash function
    block_size = 65536
    
    # Open current file in read binary mode
    with open(filename, "rb") as file_content:
        # Read first block of file
        file_block = file_content.read(block_size)
        # Repeat until no bytes left
        while len(file_block) > 0:
            file_hash.update(file_block)
            file_block = file_content.read(block_size)
            
    print("Done")
    return file_hash.hexdigest()


def getLatestSerialPath(backup_dir, serial_folder_prefix):
    print("Get latest serial name...", end="")
    # Check for serialized folders
    max_serial = 0
    found_match = False
    for foldername in os.scandir(backup_dir):
        if serial_folder_prefix in foldername.name:
            # Read serial number of folder
            current_number = int(foldername.name[len(serial_folder_prefix):])

            # Get creation date of folder
            folder_creation = datetime.utcfromtimestamp(int(os.stat(foldername).st_ctime)).strftime("%d.%m.%Y")
            # Check if creation date was today
            if folder_creation == today:
                # Set current serial and break loop
                current_serial = current_number
                found_match = True
                break
            
            if current_number > max_serial:
                max_serial = current_number
    
    if not found_match:
        current_serial = max_serial + 1

    # Define path to serial folder
    serial_folder = os.path.join(backup_dir, serial_folder_prefix + "{:02d}".format(current_serial))

    # Check if serial folder exist
    if not os.path.exists(serial_folder):
        createFolder(serial_folder)

    print(serial_folder_prefix + "{:02d}".format(current_serial))
    return serial_folder

def getLatestFileVersion(file_basename, backup_dir, serial_path):
    print(f"Getting latest file version for {file_basename}...", end="")
    # Calculate main_version by the amount of serialized folders
    main_version = 1
    for path, folders, files in os.walk(backup_dir):
        if path != serial_path:
            for filename in files:
                if file_basename in filename:
                    main_version += 1
                    break
    
    main_version /= 10
    # main_version = len(os.listdir(backup_dir)) / 10

    # Set default version
    version = 1
    # Count previous versions of file
    for filename in os.listdir(serial_path):
        if file_basename in filename:
            version += 1

    # Define subversion of file
    sub_version = "{:03d}".format(version)

    # Concat version number
    version = str(main_version) + "." + str(sub_version)
    print(version)
    return version

def writeToLog(log_path, message):
    timestamp = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    file_writer = open(log_path, "a+")
    file_writer.write(timestamp + " => " + message + "\n")
    file_writer.close()

#    _____ _               _        
#   / ____| |             | |       
#  | |    | |__   ___  ___| | _____ 
#  | |    | '_ \ / _ \/ __| |/ / __|
#  | |____| | | |  __/ (__|   <\__ \
#   \_____|_| |_|\___|\___|_|\_\___/
                                  
# Check if source_dir exists
if not (os.path.exists(source_dir) and os.path.isdir(source_dir)):
    raise Exception(f"Path does not exist or is not a directory: {source_dir}")

# Check if backup_dir exists
if not (os.path.exists(backup_dir) and os.path.isfile(backup_dir)):
    path_list = backup_dir.split("\\")
    current_path = ""
    # Recursive creation of path tree
    for i in range(len(path_list)):
        current_path += path_list[i] + "\\"
        if not os.path.exists(current_path):
            createFolder(current_path)

# # Create data folder for script if not exist
# if not os.path.exists(script_path):
#     createFolder(script_path)

# Check if script data folder exists
if not os.path.exists(script_data_folder):
    createFolder(script_data_folder)


#   ____             _                  _             _      
#  |  _ \           | |                | |           (_)     
#  | |_) | __ _  ___| | ___   _ _ __   | | ___   __ _ _  ___ 
#  |  _ < / _` |/ __| |/ / | | | '_ \  | |/ _ \ / _` | |/ __|
#  | |_) | (_| | (__|   <| |_| | |_) | | | (_) | (_| | | (__ 
#  |____/ \__,_|\___|_|\_\\__,_| .__/  |_|\___/ \__, |_|\___|
#                              | |               __/ |       
#                              |_|              |___/        

# Create empty file array
file_list = []
# Get files of source directory
for path, folders, files in os.walk(source_dir):
    for filename in files:
        # Exclude MS Office TMP data and pickle data
        if not "~" in filename and not "pickle" in filename:
            # Concat path and filename with os conform delimiter and add new path to file_list
            file_list.append(os.path.join(path, filename))
# Get hash and attribute of files to backup
file_informations, need_to_backup = getSourceFileInformations(file_list, script_data_file)

changes = False
if need_to_backup:
    # Get current serial path
    serial_path = getLatestSerialPath(backup_dir, serial_folder_prefix)

    for filename in file_informations["source"].keys():
        # Extract basename from file path
        file_basename = os.path.basename(filename)
        # Check if file needs to be backed up
        if not file_informations["source"][filename]["archived"]:
            # Check if file was backed up before
            if not filename in file_informations["backups"].keys():
                # Get current file_version
                current_file_version = getLatestFileVersion(file_basename, backup_dir, serial_path)
                
                log_message = f"Backing up {file_basename}".ljust(45)
                # Define target path
                target_path = os.path.join(serial_path, current_file_version + "=" + file_basename)
                # Copy file to backup path
                copy(filename, target_path)

                if os.path.exists(target_path):
                    log_message += "OK".center(10) + current_file_version.center(15)
                else:
                    log_message += "ERROR".center(10)

                writeToLog(backup_log, log_message)

                file_hash = getFileHash(filename)
                # Write file informations to backup dictionary
                file_informations["backups"].setdefault(filename, file_hash)
                changes = True
                # Change archived file attribute
                subprocess.run(["attrib", "+a", filename])
            else:
                # Get hash of previous backup
                previous_hash = file_informations["backups"][filename]
                file_hash = getFileHash(filename)
                # Check if hash has changed
                if previous_hash != file_hash:
                    log_message = f"Backing up {file_basename}".ljust(45)
                    # Get current file version
                    current_file_version = getLatestFileVersion(file_basename, backup_dir, serial_path)
                    # Define target path 
                    target_path = os.path.join(serial_path, current_file_version + version_delimiter + file_basename)
                    # Copy file to backup path
                    copy(filename, target_path)
                    # Overwrite file informations
                    file_informations["backups"][filename] = file_hash
                    changes = True

                    if os.path.exists(target_path):
                        log_message += "OK".center(10) + current_file_version.center(15)
                    else:
                        log_message += "ERROR".center(10)

                    writeToLog(backup_log, log_message)
                else:
                    writeToLog(backup_log, f"Skip backup of {file_basename}".ljust(45) + "Identical Hashes")
                # Change archived file attribute
                subprocess.run(["attrib", "+a", filename])
        else:
            # Write to logfile
            log_message = f"No changes in {file_basename} detected"
            writeToLog(backup_log, log_message)
else:
    # Write to logfile
    log_message = f"No changes detected"
    writeToLog(backup_log, log_message)

if changes:
    print("Save file data...", end="")
    # Save data of processed files in pickle dump
    file_writer = open(script_data_file, "wb")
    pickle.dump(file_informations["backups"], file_writer)
    file_writer.close()
    print("Done")

