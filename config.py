import sys
from pathlib import Path

DEFAULT_TITLE = "Kit Builder"

# On Linux and Windows the code needs to differ because on Linux fill='' does not give a transparent shape (for marker and edge). Here it is drawn using an xbm file instead.
# Only tested on Ubuntu 22.04.3 LTS and Windows 10/11
ON_LINUX = sys.platform.startswith("linux")

# Directory paths
BASE_DIR = Path.cwd() # base Directory
RESOURCES_DIR = BASE_DIR / "resources"
GEAR_FILE = RESOURCES_DIR / "gear.csv"
KITS_DIR = BASE_DIR / "kits"

DRUMS_ICON_PATH = RESOURCES_DIR / "Gui" / "drums_icon.png"
CYMBALS_ICON_PATH = RESOURCES_DIR / "Gui" / "cymbals_icon.png"
OTHER_ICON_PATH = RESOURCES_DIR / "Gui" / "other_icon.png"

# Set window size, adjust if needed
WINDOW_SIZE = [1200, 700]

# Canvas Size
CANVAS_WIDTH = int(WINDOW_SIZE[0])
CANVAS_HEIGHT = int(WINDOW_SIZE[1])
CANVAS_SCROLLREGION = (0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

WIDGET_PAD = 10

COLUMN_NAMES_GEAR = ["name", "type", "is_circular", "size", "flippable", "default_path", "flipped_path"] # for gear pool creation
COLUMN_NAMES = ["ID", "layer", "position", "rotation", "flipped"] # for loading/saving

# move step when using arrow keys
ARR_STEP_DEFAULT = 4
ARR_STEP_INCREMENT = 3

SPAWN_POINT = [70, 70]
TRANSPARENT_STIPPLE = '@transparent.xbm'


"""
# Commented helper code
# ["name", "type", "is_circular", "size", "flippable", "default_path", "flipped_path"]
GEAR_LIST = [["22\" Tama Bassdrum SP", "drum", 0, 25, 0, "Drums/22_tama_sp.png", "Drums/22_tama_sp.png"],###
            ["22\" Tama Bassdrum DP", "drum", 0, 25, 0, "Drums/22_tama_dp.png", "Drums/22_tama_dp.png"],###
            ["22\" Istanbul Ride", "cymbal", 1, 22, 1, "Cymbals/22_istanbul.png", "Cymbals/22_istanbul_f.png"],###
            ["22\" Paiste Flat Ride", "cymbal", 1, 22, 1, "Cymbals/22_paiste.png", "Cymbals/22_paiste_f.png"],###
            ["21\" Zildjian Ride", "cymbal", 1, 21, 1, "Cymbals/21_zildjian.png", "Cymbals/21_zildjian_f.png"],###
            ["20\" Zultan Ride", "cymbal", 1, 20, 1, "Cymbals/20_zultan.png", "Cymbals/20_zultan_f.png"],###
            ["20\" Masterwork Ride", "cymbal", 1, 20, 1, "Cymbals/20_masterwork.png", "Cymbals/20_masterwork_f.png"],###
            ["20\" Altes China", "cymbal", 1, 20, 1, "Cymbals/20_alt.png", "Cymbals/20_alt_f.png"],###
            ["19\" Sabian XSR Crash", "cymbal", 1, 19, 1, "Cymbals/19_sabian_xsr.png", "Cymbals/19_sabian_xsr_f.png"],###
            ["19\" Sabian Paragon China", "cymbal", 1, 19, 1, "Cymbals/19_sabian_paragon.png", "Cymbals/19_sabian_paragon_f.png"],###
            ["18\" Sabian HHX Crash", "cymbal", 1, 18, 1, "Cymbals/18_sabian_hhx.png", "Cymbals/18_sabian_hhx_f.png"],###
            ["18\" Sabian AAX Crash", "cymbal", 1, 18, 1, "Cymbals/18_sabian_aax.png", "Cymbals/18_sabian_aax_f.png"],###
            ["16\" Zultan Crash", "cymbal", 1, 16, 1, "Cymbals/16_zultan.png", "Cymbals/16_zultan_f.png"],###
            ["16\" Paiste PSTX Crash", "cymbal", 1, 16, 1, "Cymbals/16_paiste_pstx.png", "Cymbals/16_paiste_pstx_f.png"],###
            ["16\" Millenium China", "cymbal", 1, 16, 1, "Cymbals/16_millenium.png", "Cymbals/16_millenium_f.png"],###
            ["16\" Paiste Crash", "cymbal", 1, 16, 1, "Cymbals/16_paiste.png", "Cymbals/16_paiste_f.png"], ###
            ["16\" Tama Floortom", "drum", 1, 16, 1, "Drums/16_tama.png", "Drums/16_tama.png"],###
            ["14\" Zultan HiHat", "cymbal", 1, 14, 0, "Cymbals/14_zultan.png", "Cymbals/14_zultan.png"],###
            ["14\" Paiste HiHat", "cymbal", 1, 14, 0, "Cymbals/14_paiste.png", "Cymbals/14_paiste.png"], ###
            ["14\" Millenium Crash", "cymbal", 1, 14, 1, "Cymbals/14_millenium.png", "Cymbals/14_millenium_f.png"],###
            ["13\" Zultan HiHat", "cymbal", 1, 13, 0, "Cymbals/13_zultan.png", "Cymbals/13_zultan.png"],###
            ["13\" Tama Racktom", "drum", 1, 13, 0, "Drums/13_tama.png", "Drums/13_tama.png"],###
            ["13\" JJ Snare", "drum", 1, 13, 0, "Drums/13_pearl.png", "Drums/13_pearl.png"],###
            ["12\" Tama Racktom", "drum", 1, 12, 0, "Drums/12_tama.png", "Drums/12_tama.png"],###
            ["12\" Meinl Filter China", "cymbal", 1, 12, 1, "Cymbals/12_meinl.png", "Cymbals/12_meinl_f.png"],###
            ["12\" Wuhan China", "cymbal", 1, 12, 1, "Cymbals/12_wuhan.png", "Cymbals/12_wuhan_f.png"],###
            ["12\" Paiste Splash", "cymbal", 1, 12, 1, "Cymbals/12_paiste.png", "Cymbals/12_paiste_f.png"],###
            ["10\" Wuhan China", "cymbal", 1, 10, 1, "Cymbals/10_wuhan.png", "Cymbals/10_wuhan_f.png"],###
            ["10\" Paiste Splash", "cymbal", 1, 10, 1, "Cymbals/10_paiste.png", "Cymbals/10_paiste_f.png"],###
            ["10\" Gretsch Snare", "drum", 1, 10, 0, "Drums/10_gretsch.png", "Drums/10_gretsch.png"],###
            ["8\" Zultan Splash", "cymbal", 1, 8, 1, "Cymbals/8_zultan.png", "Cymbals/8_zultan_f.png"],###
            ["8\" Zultan Splash (Broken)", "cymbal", 1, 8, 1, "Cymbals/8_zultan_broken.png", "Cymbals/8_zultan_broken_f.png"],###
            ["8\" Paiste Bell", "cymbal", 1, 8, 1, "Cymbals/8_paiste.png", "Cymbals/8_paiste_f.png"],###
            ["8\" Meinl Ching Ring", "other", 1, 8, 1, "Other/8_meinl_ching.png", "Other/8_meinl_ching.png"],###
            ["6\" Stagg Splash (Thin)", "cymbal", 1, 6, 1, "Cymbals/6_stagg_thin.png", "Cymbals/6_stagg_thin_f.png"],###
            ["6\" Stagg Splash (Heavy)", "cymbal", 1, 6, 1, "Cymbals/6_stagg_heavy.png", "Cymbals/6_stagg_heavy_f.png"],###
            ["6\" Stagg Bell", "cymbal", 1, 6, 1, "Cymbals/6_stagg_bell.png", "Cymbals/6_stagg_bell_f.png"],###
            ["6\" Octoban (High)", "drum", 1, 6, 0, "Drums/6_octoban_low.png", "Drums/6_octoban_low.png"],###
            ["6\" Octoban (Low)", "drum", 1, 6, 0, "Drums/6_octoban_low.png", "Drums/6_octoban_low.png"],###
            ["Sonor Throne", "other", 1, 12, 0, "Other/throne.png", "Other/throne.png"],###
            ["Pearl HiHat Machine", "other", 0, 26, 0, "Other/pearl_tilted.png", "Other/pearl_tilted.png"],###
            ["Pearl Left Pedal", "other", 0, 13, 0, "Other/pearl_lp.png", "Other/pearl_lp.png"],###
            ["Pearl Cowbell", "other", 0, 9, 0, "Other/pearl_cowbell.png", "Other/pearl_cowbell.png"]]###
    
import csv
def write_gear_file():
    #(Re-)write the gear.csv file from GEAR_LIST
    if True:
        # File does not exists
        with open(GEAR_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=COLUMN_NAMES_GEAR)
            writer.writeheader()
    
    for k in GEAR_LIST:
        new_element = {"name": k[0], "type": k[1], "is_circular": k[2], "size": k[3], "flippable": k[4], "default_path": k[5], "flipped_path": k[6]}
        with open(GEAR_FILE, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=COLUMN_NAMES_GEAR)
            writer.writerow(new_element)
    

# (Re-)write the gear.csv file
write_gear_file()
"""