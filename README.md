
# Datheon Python Programming Internship

## Task 1: Hangman Word Guessing Game

A modular, terminal-based Hangman game developed in Python as part of the Datheon Python Programming Internship.

## Features

- Random secret word selection
- Six incorrect attempts per round
- Progressive ASCII Hangman drawings
- Masked word display with correctly guessed letters
- Tracking of previously guessed letters
- Duplicate-guess prevention
- Input validation
- Win and loss detection
- Replay functionality

## Technologies Used

- Python 3
- random module
- Core Python data structures and control flow

## Requirements

Python 3.10 or later is recommended.
No external packages are required.

## How to Run

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Run:

   ```bash
   python hangman.py
   ```

   On Windows, you can also use `py hangman.py`.

## Project Structure

```text
Datheon_Python_Programming_Internship/
├── hangman.py
├── README.md
├── requirements.txt
├── .gitignore
└── screenshots/
```

## Concepts Practiced

Functions, loops, conditionals, strings, sets, lists,
randomization, input validation, and modular programming.

## Learning Outcome

This project demonstrates foundational Python programming
skills through an interactive console-based game.


## Task 2: Stock Portfolio Performance Tracker

A Python command-line application for tracking stock holdings,
calculating portfolio returns, and saving performance reports.

### Features

- Stock ticker validation using a company constituents CSV
- Offline demonstration prices and optional live price retrieval
- Portfolio positions stored in a dictionary
- Weighted average purchase cost for repeated stock entries
- Per-holding and overall profit/loss calculations
- Percentage return calculations
- Persistent CSV performance logs

### Files

- `portfolio.py` - Main application
- `constituents.csv` - Company and ticker reference
- `sample_prices.csv` - Illustrative offline prices
- `portfolio_summary.csv` - Generated performance reports
- `requirements.txt` - Optional live-price dependency

### Run

```bash
python portfolio.py
```

For live quotes, install the optional dependency:

```bash
python -m pip install yfinance
```

### Financial Calculation

Invested Capital = Purchase Price × Number of Shares

Market Value = Current Price × Number of Shares

Profit/Loss = Market Value - Invested Capital

Return (%) = (Profit/Loss / Invested Capital) × 100

### Limitations

Sample prices are fictional and must not be used for investment
decisions. Live quotes depend on the external data provider.
This educational tool excludes brokerage fees, taxes, and dividends.


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
