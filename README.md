# python-drum-kit-builder
Software development of a virtual drum kit building tool in python. 

## Motivation
Several virtual drum kit building applications can be found on the internet. They are fun to use, but mostly lack options for personalization. This project offers an alternative that can be used locally and allows the user to customize the gear available in the editor (for example with images of owned instruments). Designed kits can be saved and edited. The planning of gigs, sessions etc. with custom instruments is effortless and fun!

## Project Structure
- `scripts/`: core code and standalone setup
- `resources/`: image files
- `kits/`: saved example kits

## Tools
- Python
- tkinter, customtkinter
- PIL, os, csv, pathlib, math, ast
- cx_Freeze

## How to Run
pip install -r requirements.txt  
python scripts/kit_builder.py
Create standalone version: python scripts/SCsetup.py

## Notes
- If you want to be able to run the editor on a system without Python or all of the nescessary packages, you can create a standalone version with cx_Freeze (using SCsetup.py), or generate a standalone version with your prefered method.
- Instructions on how to customize instruments will be provided in the future. Users with some knowledge of Python
may be able to follow the comments in the script.

## Future Improvements
- Simplify parts of the code
- Improve user friendliness (In-editor instrument management, flexible window size and shape)
- Improve optics
- Add feaures (instructions, background change, add sample sounds)
