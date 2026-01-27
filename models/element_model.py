# Element Model: handling element state

class ElementModel:
    def __init__(self, instr, layer, pos, rot=0, flipped=False):
        self.instr = instr
        self.layer = layer
        self.pos = pos
        self.rot = rot
        self.flipped = flipped
        self.is_selected = False
        self.drag_data_x = 0
        self.drag_data_y = 0
        self.polygon_points = []
        if not self.instr.is_circular:
            # Polygon points always center around (0,0)
            self.polygon_points = [-self.instr.r, 
                                   -self.instr.r, 
                                   -self.instr.r, 
                                   +self.instr.r, 
                                   +self.instr.r, 
                                   +self.instr.r, 
                                   +self.instr.r, 
                                   -self.instr.r]

    def move(self, dx, dy):
        """ Set element position data """
        x, y = self.pos
        new_pos = [x + dx, y + dy]
        self.pos = new_pos