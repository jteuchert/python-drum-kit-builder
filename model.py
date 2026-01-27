# Model: handling the application state and data

from models.instrument import Instrument
import config
from utils import csv_io

class AppState:
    def __init__(self, number: float):
        self.instruments = [] # index is the instrument ID
        self.elements = {} # dictionary of elements, key is layer
        self.hovering = 0 # layer of element, above which mouse is hovering, 0 if None
        self.selected = 0 # selected layer, 0 if None
        self.all_selected = False # If all elements are selected via all_button
        self.save_path = None
        self.arr_step = config.ARR_STEP_DEFAULT


    def load_instruments_from_csv(self, path):
        """ (Re-)load instruments list from CSV file """
        self.instruments.clear()
        num_instruments = csv_io.get_row_count_from_csv(self, path)
        for idx in range(num_instruments):
            instrument = Instrument(idx)
            self.instruments.append(instrument)


    def reset_state(self):
        """ Reset project-relevant state variables """
        self.elements = {}
        self.hovering = 0
        self.selected = 0
        self.all_selected = False
        self.save_path = None