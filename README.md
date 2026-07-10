# File Organizer

A simple Python script to automatically organize files by type. It scans a folder, detects extensions, and moves files into categorized subfolders (Documents, Images, Code, Archives, etc.).

## Features
- Sorts files by extension
- Handles duplicates safely
- Logs all actions
- Dry-run mode for preview

## Usage
```bash
python file_organizer.py "C:\path\to\your\folder"
python file_organizer.py "C:\path\to\your\folder" --dry-run
Documents/
    notes.txt
    report.pdf
Images/
    photo.jpg
Archives/
    backup.zip
Other/
    desktop.ini
