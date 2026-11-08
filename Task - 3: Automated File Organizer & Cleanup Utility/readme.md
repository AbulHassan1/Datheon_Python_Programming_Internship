
## Task 3: Automated File Organizer & Cleanup Utility

A Python desktop automation utility that sorts files into
category folders according to their extensions.

### Features

- Automatic sorting into Documents, Images, Videos,
  Archives, and Code
- Directory scanning with os.scandir()
- File movement using shutil.move()
- Automatic destination folder creation
- Collision-safe destination filenames
- Permission and filesystem exception handling
- Dry-run preview mode
- Execution summary with moved, skipped, and failed counts

### Technologies

- Python 3
- os
- shutil
- pathlib
- argparse
- collections.Counter

### How to Run

Preview the changes first:

```bash
python organizer.py "C:\path\to\test_files"
```

Apply the changes after reviewing the preview:

```bash
python organizer.py "C:\path\to\test_files" --apply
```

### Safety Notes

The utility organizes files in the selected directory's
top level. It does not recursively process subdirectories.
Unknown extensions are skipped, and existing files are
not intentionally overwritten.

Test with sample files before organizing important folders.