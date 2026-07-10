import argparse
from pathlib import Path
import shutil
import logging

# Configure logging
logging.basicConfig(filename='organizer.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# File type mapping (expand as needed)
CATEGORIES = {
    ".py": "Python_Code",
    ".txt": "Documents",
    ".pdf": "Documents",
    ".docx": "Documents",
    ".doc": "Documents",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".pptx": "Presentations",
    ".ppt": "Presentations",
    ".xlsx": "Spreadsheets",
    ".xls": "Spreadsheets",
    ".csv": "Spreadsheets",
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".mp3": "Audio",
    ".wav": "Audio",
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos"
}

def organize_directory(source: Path, dry_run: bool = False):
    for item in source.glob("*"):
        if item.is_file():
            ext = item.suffix.lower()
            category = CATEGORIES.get(ext, "Other")
            target_dir = source / category

            if not target_dir.exists():
                logging.info(f"Creating directory: {target_dir}")
                if not dry_run:
                    target_dir.mkdir()

            target_path = target_dir / item.name
            if target_path.exists():
                # Conflict resolution
                new_name = f"{item.stem}_copy{item.suffix}"
                target_path = target_dir / new_name

            logging.info(f"Moving {item} → {target_path}")
            if not dry_run:
                try:
                    shutil.move(str(item), str(target_path))
                except PermissionError:
                    logging.error(f"Permission denied: {item}")
                except Exception as e:
                    logging.error(f"Error moving {item}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated File Organizer")
    parser.add_argument("source", help="Directory to organize")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without moving files")
    args = parser.parse_args()

    organize_directory(Path(args.source), args.dry_run)
