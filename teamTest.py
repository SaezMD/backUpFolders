# Implementation of a program that synchronizes two folders: source and replica.
# Language: Python 3
"""
* One-way sync
* Sync must be periodically
* Logged to file and console: file creation, file copy, file removal.
* Folder paths, synchronization interval and lof file path ----> command line arguments
* 
"""
#!/usr/bin/python3
import os
import time
import argparse
import logging
import hashlib
import shutil

#check partial files, open files and temporary

#check huge files > exfat


def compareBysha256(file01, file02)-> bool:
    """This function compares 2 files by the sha256 hash"""
    with open(file01, "rb") as f01, open(file02, "rb") as f02:
        return hashlib.sha256(f01.read()).hexdigest() == hashlib.sha256(f02.read()).hexdigest()


def compare(directory1, directory2):
    """this function compares 2 directories with all the files inside both of them"""
    originFiles = os.listdir(directory1)
    destinationFiles = os.listdir(directory2)

    for file in originFiles:
        originFilesPath = os.path.join(directory1, file)
        destinationFilesPath = os.path.join(directory2, file)

        if file in destinationFiles:
            if compareBysha256(originFilesPath, destinationFilesPath):
                comparationMessage = f"{file} did NOT change. File not copied to the backup directory."
            else:
                os.remove(destinationFilesPath)
                shutil.copy2(originFilesPath, destinationFilesPath)
                comparationMessage = f"{file} updated."
        else:
            shutil.copy2(originFilesPath, destinationFilesPath)
            comparationMessage = f"{file} copied to backup directory as new file."

        logger.info(comparationMessage)
        print(comparationMessage)

    #purge OLD files in destination and not present in the origin anymore.
    for file in destinationFiles:
        if file not in originFiles:
            os.remove(os.path.join(directory2, file))
            purgeMessage = f"{file} has been purged."
            logger.info(purgeMessage)
            print(purgeMessage)


def backupFiles(originFolder: str, destinationFolder: str, timeWait:int, logFilePath):
    """this function makes the one-way backup from origin folder to destination. The function save all the logs in a separate log file."""

    startMessage = f"Starting backup. Origin: {originFolder}, backup destination: {destinationFolder}, time to wait between backups: {timeWait} seconds, log file name: {logFilePath}"
    logger.info(startMessage)
    print(startMessage) #console

    while True:
            compare(originFolder,destinationFolder)
            time.sleep(timeWait)
    """
        try:
            compare(originFolder,destinationFolder)
            time.sleep(timeWait)
        except:
            raise Exception("Something is not working. Please check log for more details.")
        """

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
    if timeToWait < 60 and timeToWait > 0:
        print(f"Sync period of time changed from: {timeToWait} to: 60 seconds.")
        timeToWait = 60 # minimun is 60 seconds (1 minute)    
    elif timeToWait <= 0:
        raise argparse.ArgumentError(None,"Interval time is not correct! Please check it.")

    #check if origin folder exists
    if not os.path.isdir(args.origin):
        raise argparse.ArgumentError(None, "Origin folder does NOT exist! Please check it.")
    
    #check if destination folder exists
    if not os.path.isdir(args.destination):
        os.makedirs(args.destination)


    #check if logFilePath is OK
    if not args.logFile.endswith("log") or args.logFile.endswith("txt"):
        raise argparse.ArgumentError(None,"Logfile type is not correct! Please use '.txt' or '.log'.") 
    
    #logger in a file
    logger = logging.getLogger("backupFolders")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
    fileHandler = logging.FileHandler(args.logFile) # to send to a file -> create the file
    fileHandler.setFormatter(formatter) # to send to a file
    logger.addHandler(fileHandler) # to send to a file

    backupFiles(args.origin, args.destination, timeToWait, args.logFile)

