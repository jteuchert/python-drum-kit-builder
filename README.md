# python-drum-kit-builder
Software development of a virtual drum kit building tool in python. 

![preview](Preview.png)

## Motivation
Several virtual drum kit building applications can be found on the internet. They are fun to use, but mostly lack options for personalization. This project offers an alternative that can be used locally and allows the user to customize the gear available in the editor (for example with images of owned instruments). Designed kits can be saved and edited. The planning of gigs, sessions etc. with custom instruments is effortless and fun.

## Project Structure
- `resources/`: image files and gear.csv
- `kits/`: saved example kits
- core script and additional files in root folder

## Tools
- Python
- Python native packages
- tkinter, customtkinter
- PIL
- cx_Freeze

## How to Run
The scripts were tested on Linux (Ubuntu) and Win10/11.
Some Python packages (and Python itself) need to be installed to run the code.

Linux Dependencies:

This project uses tkinter for the GUI.
On Linux, tkinter may not be installed by default.
Install it using your system package manager:

### Ubuntu / Debian
`sudo apt install python3-tk`

### Fedora
`sudo dnf install python3-tkinter`

### Arch
`sudo pacman -S tk`

Then install Python dependencies:
`pip install -r requirements.txt`

Run the core script:
`python scripts/kit_builder_v1.py`

On Ubuntu you can alternatively simply run the test_install.sh file (might take a minute to run):
`bash test_install.sh`

(Optional) Create standalone version (install cx_Freeze first):
`python scripts/SCsetup.py`


## Features
With this editor you can design virtual drum kits using custom images of your owned (or other) gear. You can:
- change any items layer
- rotate items and flip cymbals
- save and load kits to files
- move around items with the mouse or arrow keys
- adjust key movement step size

## Notes
- If you want to be able to run the editor on a system without Python or all of the nescessary packages, you can create a standalone version with cx_Freeze (using SCsetup.py), or generate a standalone version with your prefered method.
- Instructions on how to customize instruments will be provided in the future. Users with some knowledge of Python
may be able to follow helpful comments in the scripts.

## Future Improvements
- Simplify parts of the code
- Improve user friendliness (In-editor instrument management, flexible window size and shape, guided notebook for adding instruments)
- Improve optics
- Add feaures (instructions, background change, add sample sounds)
