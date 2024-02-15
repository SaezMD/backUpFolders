This repository includes the pyhton files to backup files from one folder to another.

Features:
* One-way sync
* Sync must be performed periodically
* Logged to file and console: file creation, file copy, file removal.
* Folder paths, synchronization interval and log file path ----> command line arguments
* Comparation is made by: SHA256 hash

Extra Features:
- Check if time to wait is OK ( > 0 ) and ( > 10 seconds).
- Check if origin folder exists (if not: raise an error).
- Check if destination folder exists (if not: the program creates the folder)
- Check if logger file extension is OK. (if not: raise an error).
- Important: the backup is performance in all the files, including SUBFOLDERS.

