# Implementation of a program that synchronizes two folders: source and replica.
# Language: Python 3
"""
* One-way sync
* Sync must be periodically
* Logged to file and console: file creation, file copy, file removal.
* Folder paths, synchronization interval and lof file path ----> command line arguments
"""

#!/usr/bin/python3
import logging
from logging.handlers import RotatingFileHandler

import os
import time
import argparse
import hashlib
import shutil

#check partial files, open files and temporary

#check huge files > exfat


def compareBysha256(file01, file02)-> bool:
    """This function compares 2 files by the sha256 hash"""
    with open(file01, "rb") as f01, open(file02, "rb") as f02: #you have to open the file and close it using with
        return hashlib.sha256(f01.read()).hexdigest() == hashlib.sha256(f02.read()).hexdigest()


def compare(directory1, directory2):
    """This function compares two directories, including all files inside them (including subfolders). """
    for root, _, files in os.walk(directory1): #walk ALL files in the folder
        for file in files:
            originFilesPath = os.path.join(root, file)
            relativePath = os.path.relpath(originFilesPath, directory1)
            destinationFilesPath = os.path.join(directory2, relativePath)

            if os.path.exists(destinationFilesPath): #if the file exist in destinatio, check by comparation
                if not compareBysha256(originFilesPath, destinationFilesPath):
                    #comparationMessage = f"{relativePath} did NOT change. File not copied to the backup directory."
                    os.remove(destinationFilesPath) #remove the old version
                    shutil.copy2(originFilesPath, destinationFilesPath) # copy the new version
                    comparationMessage = f"{relativePath} updated."
                    logger.info(comparationMessage)
                    print(comparationMessage)
            else:
                os.makedirs(os.path.dirname(destinationFilesPath), exist_ok=True) #create the folder in case need it
                shutil.copy2(originFilesPath, destinationFilesPath) #copy the file becasuse there is no previos version in the destination folder
                comparationMessage = f"{relativePath} copied to backup directory as a new file."
                logger.info(comparationMessage)
                print(comparationMessage)

    # Purge OLD files in destination that are no longer present in the origin. Also subfolders.
    for root, dirs, files in os.walk(directory2, topdown=False):
        for file in files:
            destination_path = os.path.join(root, file)
            relative_path = os.path.relpath(destination_path, directory2) #relative as aux. 
            original_path = os.path.join(directory1, relative_path)

            if not os.path.exists(original_path):
                if os.path.isfile(destination_path): #remove only files
                    os.remove(destination_path)
                    purgeMessage = f"{destination_path} has been purged."
                elif os.path.isdir(destination_path): #remove directories and all files (not logged)
                    shutil.rmtree(destination_path)
        
                logger.info(purgeMessage)
                print(purgeMessage)

        for dirName in dirs: #remove directories nor present in origin
            destinationDir = os.path.join(root, dirName)
            relativeDir = os.path.relpath(destinationDir, directory2)
            originalDir = os.path.join(directory1, relativeDir)

            if not os.path.exists(originalDir):
                shutil.rmtree(destinationDir)

def backupFiles(originFolder: str, destinationFolder: str, timeWait:int, logFilePath):
    """this function makes the one-way backup from origin folder to destination. The function save all the logs in a separate log file."""

    startMessage = f"Starting backup. Origin: {originFolder}, backup destination: {destinationFolder}, time to wait between backups: {timeWait} seconds, log file name: {logFilePath}"
    logger.info(startMessage)
    print(startMessage) #console

    while True: #to make it run periodically
        try: #to raise error when there is a problem
            compare(originFolder,destinationFolder)
            time.sleep(timeWait)
        except:
            raise Exception("Something is not working. Please check log for more details.")

if __name__ == '__main__':
    #enter data by arguments
    parser = argparse.ArgumentParser(description='One way backup program')
    parser.add_argument('--origin', type=str, default="origin", help='Origin of the path')
    parser.add_argument('--destination', type=str, default="destination", help='Destination of the backup.')
    parser.add_argument('--time', type=int, default=300, help='Sync period of time in seconds (Defaul= 5 minutes).')
    parser.add_argument('--logFile', type=str, default='logfile.log', help='Path for the log file (Default = logfile.log).')
    args = parser.parse_args()

    #check if time to wait is OK
    timeToWait = args.time
    if timeToWait < 10 and timeToWait > 0:
        print(f"Sync period of time changed from: {timeToWait} to: 10 seconds.")
        timeToWait = 10 # minimun is 10 seconds. Giving some time to the machine.    
    elif timeToWait <= 0:
        raise argparse.ArgumentError(None,"Interval time is not correct! Please check it.")

    #check if origin folder exists
    if not os.path.isdir(args.origin):
        raise argparse.ArgumentError(None, "Origin folder does NOT exist! Please check it.")
    
    #check if destination folder exists
    if not os.path.isdir(args.destination):
        os.makedirs(args.destination)

    #check if logFile name is OK
    if not args.logFile.endswith("log") or args.logFile.endswith("txt"):
        raise argparse.ArgumentError(None,"Logfile type is not correct! Please use '.txt' or '.log'") 
    
    #logger in a file
    logger = logging.getLogger("backupFolders Rotating")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
    # to send to a file -> create the file y rotating mode
    fileHandler = RotatingFileHandler(args.logFile, maxBytes=200000000, backupCount=5) #200MB limit for each file. x5 MAX
    fileHandler.setFormatter(formatter) # to send to a file with format
    logger.addHandler(fileHandler) # to send to a file


    backupFiles(args.origin, args.destination, timeToWait, args.logFile)

