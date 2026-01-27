from config import GEAR_FILE, RESOURCES_DIR
from utils.csv_io import get_row_from_csv

class Instrument:
    """ All gear, each element with its properties """
    def __init__(self, idx):
        row = get_row_from_csv(GEAR_FILE, idx)
        self.is_used = False
        self.ID = idx        
        self.name = row["name"]
        self.type = row["type"]
        self.is_circular = row["is_circular"] == "1"
        self.size = int(row["size"])
        self.r = 4.95*self.size
        self.flippable = row["flippable"] == "1"
        self.default_path = RESOURCES_DIR / row["default_path"]
        self.flipped_path = RESOURCES_DIR / row["flipped_path"]