import sys
from pathlib import Path

# On Linux and Windows the code needs to differ because on Linux fill='' does not give a transparent shape (for marker and edge). Here it is drawn using an xbm file instead.
# Only tested on Ubuntu 22.04.3 LTS and Windows 10/11
ON_LINUX = sys.platform.startswith("linux")

# Directory paths
#BASE_DIR = os.getcwd() # base Directory
BASE_DIR = Path.cwd()
RESOURCES_DIR = BASE_DIR / "resources"
GEAR_FILE = RESOURCES_DIR / "gear.csv"
KITS_DIR = BASE_DIR / "kits"

# Set window size, adjust if needed
WINDOW_SIZE = [1200, 700]

COLUMN_NAMES_GEAR = ["name", "type", "is_circular", "size", "flippable", "default_path", "flipped_path"] # for gear pool creation
COLUMN_NAMES = ["ID", "layer", "position", "rotation", "flipped"] # for loading/saving

# move step when using arrow keys
ARR_STEP_DEFAULT = 1

SPAWN_POINT = [50, 50]
TRANSPARENT_STIPPLE = '@transparent.xbm'

# ["name", "type", "is_circular", "size", "flippable", "default_path", "flipped_path"]
GEAR_LIST = [["22\" Tama Bassdrum SP", "drum", 0, 25, 0, "Drums/22_tama_sp.png", "Drums/22_tama_sp.png"],###
            ["22\" Tama Bassdrum DP", "drum", 0, 25, 0, RESOURCES_DIR / "Drums" / "22_tama_dp.png", RESOURCES_DIR / "Drums" / "22_tama_dp.png"],###
            ["22\" Istanbul Ride", "cymbal", 1, 22, 1, RESOURCES_DIR / "Cymbals" / "22_istanbul.png", RESOURCES_DIR / "Cymbals" / "22_istanbul_f.png"],###
            ["22\" Paiste Flat Ride", "cymbal", 1, 22, 1, RESOURCES_DIR / "Cymbals" / "22_paiste.png", RESOURCES_DIR / "Cymbals" / "22_paiste_f.png"],###
            ["21\" Zildjian Ride", "cymbal", 1, 21, 1, RESOURCES_DIR / "Cymbals" / "21_zildjian.png", RESOURCES_DIR / "Cymbals" / "21_zildjian_f.png"],###
            ["20\" Zultan Ride", "cymbal", 1, 20, 1, RESOURCES_DIR / "Cymbals" / "20_zultan.png", RESOURCES_DIR / "Cymbals" / "20_zultan_f.png"],###
            ["20\" Masterwork Ride", "cymbal", 1, 20, 1, RESOURCES_DIR / "Cymbals" / "20_masterwork.png", RESOURCES_DIR / "Cymbals" / "20_masterwork_f.png"],###
            ["20\" Altes China", "cymbal", 1, 20, 1, RESOURCES_DIR / "Cymbals" / "20_alt.png", RESOURCES_DIR / "Cymbals" / "20_alt_f.png"],###
            ["19\" Sabian XSR Crash", "cymbal", 1, 19, 1, RESOURCES_DIR / "Cymbals" / "19_sabian_xsr.png", RESOURCES_DIR / "Cymbals" / "19_sabian_xsr_f.png"],###
            ["19\" Sabian Paragon China", "cymbal", 1, 19, 1, RESOURCES_DIR / "Cymbals" / "19_sabian_paragon.png", RESOURCES_DIR / "Cymbals" / "19_sabian_paragon_f.png"],###
            ["18\" Sabian HHX Crash", "cymbal", 1, 18, 1, RESOURCES_DIR / "Cymbals" / "18_sabian_hhx.png", RESOURCES_DIR / "Cymbals" / "18_sabian_hhx_f.png"],###
            ["18\" Sabian AAX Crash", "cymbal", 1, 18, 1, RESOURCES_DIR / "Cymbals" / "18_sabian_aax.png", RESOURCES_DIR / "Cymbals" / "18_sabian_aax_f.png"],###
            ["16\" Zultan Crash", "cymbal", 1, 16, 1, RESOURCES_DIR / "Cymbals" / "16_zultan.png", RESOURCES_DIR / "Cymbals" / "16_zultan_f.png"],###
            ["16\" Paiste PSTX Crash", "cymbal", 1, 16, 1, RESOURCES_DIR / "Cymbals" / "16_paiste_pstx.png", RESOURCES_DIR / "Cymbals" / "16_paiste_pstx_f.png"],###
            ["16\" Millenium China", "cymbal", 1, 16, 1, RESOURCES_DIR / "Cymbals" / "16_millenium.png", RESOURCES_DIR / "Cymbals" / "16_millenium_f.png"],###
            ["16\" Paiste Crash", "cymbal", 1, 16, 1, RESOURCES_DIR / "Cymbals" / "16_paiste.png", RESOURCES_DIR / "Cymbals" / "16_paiste_f.png"], ###16
            ["16\" Tama Floortom", "drum", 1, 16, 1, RESOURCES_DIR / "Drums" / "16_tama.png", RESOURCES_DIR / "Drums" / "16_tama.png"],###
            ["14\" Zultan HiHat", "cymbal", 1, 14, 0, RESOURCES_DIR / "Cymbals" / "14_zultan.png", RESOURCES_DIR / "Cymbals" / "14_zultan.png"],###
            ["14\" Paiste HiHat", "cymbal", 1, 14, 0, RESOURCES_DIR / "Cymbals" / "14_paiste.png", RESOURCES_DIR / "Cymbals" / "14_paiste.png"], ### paiste
            ["14\" Millenium Crash", "cymbal", 1, 14, 1, RESOURCES_DIR / "Cymbals" / "14_millenium.png", RESOURCES_DIR / "Cymbals" / "14_millenium_f.png"],###
            ["13\" Zultan HiHat", "cymbal", 1, 13, 0, RESOURCES_DIR / "Cymbals" / "13_zultan.png", RESOURCES_DIR / "Cymbals" / "13_zultan.png"],###
            ["13\" Tama Racktom", "drum", 1, 13, 0, RESOURCES_DIR / "Drums" / "13_tama.png", RESOURCES_DIR / "Drums" / "13_tama.png"],###
            ["13\" JJ Snare", "drum", 1, 13, 0, RESOURCES_DIR / "Drums" / "13_pearl.png", RESOURCES_DIR / "Drums" / "13_pearl.png"],###
            ["12\" Tama Racktom", "drum", 1, 12, 0, RESOURCES_DIR / "Drums" / "12_tama.png", RESOURCES_DIR / "Drums" / "12_tama.png"],###
            ["12\" Meinl Filter China", "cymbal", 1, 12, 1, RESOURCES_DIR / "Cymbals" / "12_meinl.png", RESOURCES_DIR / "Cymbals" / "12_meinl_f.png"],###
            ["12\" Wuhan China", "cymbal", 1, 12, 1, RESOURCES_DIR / "Cymbals" / "12_wuhan.png", RESOURCES_DIR / "Cymbals" / "12_wuhan_f.png"],###
            ["12\" Paiste Splash", "cymbal", 1, 12, 1, RESOURCES_DIR / "Cymbals" / "12_paiste.png", RESOURCES_DIR / "Cymbals" / "12_paiste_f.png"],###
            ["10\" Wuhan China", "cymbal", 1, 10, 1, RESOURCES_DIR / "Cymbals" / "10_wuhan.png", RESOURCES_DIR / "Cymbals" / "10_wuhan_f.png"],###
            ["10\" Paiste Splash", "cymbal", 1, 10, 1, RESOURCES_DIR / "Cymbals" / "10_paiste.png", RESOURCES_DIR / "Cymbals" / "10_paiste_f.png"],###
            ["10\" Gretsch Snare", "drum", 1, 10, 0, RESOURCES_DIR / "Drums" / "10_gretsch.png", RESOURCES_DIR / "Drums" / "10_gretsch.png"],###
            ["8\" Zultan Splash", "cymbal", 1, 8, 1, RESOURCES_DIR / "Cymbals" / "8_zultan.png", RESOURCES_DIR / "Cymbals" / "8_zultan_f.png"],###
            ["8\" Zultan Splash (Broken)", "cymbal", 1, 8, 1, RESOURCES_DIR / "Cymbals" / "8_zultan_broken.png", RESOURCES_DIR / "Cymbals" / "8_zultan_broken_f.png"],###
            ["8\" Paiste Bell", "cymbal", 1, 8, 1, RESOURCES_DIR / "Cymbals" / "8_paiste.png", RESOURCES_DIR / "Cymbals" / "8_paiste_f.png"],###
            ["8\" Meinl Ching Ring", "other", 1, 8, 1, RESOURCES_DIR / "Other" / "8_meinl_ching.png", RESOURCES_DIR / "Other" / "8_meinl_ching.png"],###
            ["6\" Stagg Splash (Thin)", "cymbal", 1, 6, 1, RESOURCES_DIR / "Cymbals" / "6_stagg_thin.png", RESOURCES_DIR / "Cymbals" / "6_stagg_thin_f.png"],###1st
            ["6\" Stagg Splash (Heavy)", "cymbal", 1, 6, 1, RESOURCES_DIR / "Cymbals" / "6_stagg_heavy.png", RESOURCES_DIR / "Cymbals" / "6_stagg_heavy_f.png"],###2nd
            ["6\" Stagg Bell", "cymbal", 1, 6, 1, RESOURCES_DIR / "Cymbals" / "6_stagg_bell.png", RESOURCES_DIR / "Cymbals" / "6_stagg_bell_f.png"],###
            ["6\" Octoban (High)", "drum", 1, 6, 0, RESOURCES_DIR / "Drums" / "6_octoban_low.png", RESOURCES_DIR / "Drums" / "6_octoban_low.png"],###1st
            ["6\" Octoban (Low)", "drum", 1, 6, 0, RESOURCES_DIR / "Drums" / "6_octoban_low.png", RESOURCES_DIR / "Drums" / "6_octoban_low.png"],###2nd
            ["Sonor Throne", "other", 1, 12, 0, RESOURCES_DIR / "Other" / "throne.png", RESOURCES_DIR / "Other" / "throne.png"],###
            ["Pearl HiHat Machine", "other", 0, 26, 0, RESOURCES_DIR / "Other" / "pearl_tilted.png", RESOURCES_DIR / "Other" / "pearl_tilted.png"],###
            ["Pearl Left Pedal", "other", 0, 13, 0, RESOURCES_DIR / "Other" / "pearl_lp.png", RESOURCES_DIR / "Other" / "pearl_lp.png"],
            ["Pearl Cowbell", "other", 0, 9, 0, RESOURCES_DIR / "Other" / "pearl_cowbell.png", RESOURCES_DIR / "Other" / "pearl_cowbell.png"]]###
    