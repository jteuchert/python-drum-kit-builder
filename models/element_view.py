# Element View: handling element visuals

from utils import image_utils
import config 

class ElementView:
    def __init__(self, canvas, el_model):
        self.canvas = canvas
        self.el_model = el_model

        self.texture = self._load_texture()
        self.image = self.canvas.create_image(
            *el_model.pos, anchor="center", image=self.texture
        )


    def bind_marker(self, *, enter=None, leave=None, drag_start=None, drag_stop=None, drag=None):
        """ Bind events to the marker """
        self.canvas.tag_bind(self.marker, "<Enter>", enter)
        self.canvas.tag_bind(self.marker, "<Leave>", leave)
        self.canvas.tag_bind(self.marker, "<ButtonPress-1>", drag_start)
        self.canvas.tag_bind(self.marker, "<ButtonRelease-1>", drag_stop)
        self.canvas.tag_bind(self.marker, "<B1-Motion>", drag)


    def _load_texture(self):
        """ Load canvas element texture """
        path = (
            self.el_model.instr.flipped_path
            if self.el_model.flipped
            else self.el_model.instr.default_path
        )
        return image_utils.instrument_image(path, self.el_model.rot)
    
    def update_texture(self):
        """ Update elements' texture on canvas """
        self.texture = self._load_texture()
        self.canvas.itemconfig(self.image, image=self.texture)


    def set_edge_and_marker(self, is_circular, r, pos):
        """ Set up edge and marker on canvas """
        if is_circular:
            # Create circle
            self.edge = self.draw_circle(r, pos)
            self.marker = self.draw_circle(r, pos)
        else:
            # Create polygon (square)
            self.edge = self.draw_polygon(self.el_model.polygon_points)
            self.marker = self.draw_polygon(self.el_model.polygon_points)
            self.canvas.move(self.marker, pos[0], pos[1])
            self.canvas.move(self.edge, pos[0], pos[1])

    def draw_circle(self, r, pos):
        """ Draw and return circle on canvas with given radius and position """
        circle = self.canvas.create_oval(
                pos[0]-r, 
                pos[1]-r, 
                pos[0]+r, 
                pos[1]+r, 
                width=3, 
                outline=''
            )
        if config.ON_LINUX:
            self.canvas.itemconfig(circle, fill='gray')
            self.canvas.itemconfig(circle, stipple=config.TRANSPARENT_STIPPLE)
        else:
            self.canvas.itemconfig(circle, fill='')
        return circle
    
    def draw_polygon(self, polygon_points):
        """ Draw and return square on canvas with given polygon points """
        polygon = self.canvas.create_polygon(
                polygon_points, 
                width=3, 
                outline=''
            )
        
        if config.ON_LINUX:
            self.canvas.itemconfig(polygon, fill='gray')
            self.canvas.itemconfig(polygon, stipple=config.TRANSPARENT_STIPPLE)
        else:
            self.canvas.itemconfig(polygon, fill='')
        return polygon


    def highlight(self, event):
        """ Highlight self with red outline """
        self.canvas.itemconfig(self.edge, outline='red')

    def dehighlight(self, event):
        """ Un-highlight self """
        self.canvas.itemconfig(self.edge, outline='')


    def move(self, dx, dy):
        """ Move image, marker and edge on canvas """
        self.canvas.move(self.image, dx, dy)
        self.canvas.move(self.edge, dx, dy)
        self.canvas.move(self.marker, dx, dy)


    def get_canvas_borders(self):
        """ Get and return real canvas size """
        canv_width = self.canvas.winfo_width()
        canv_height = self.canvas.winfo_height()
        return canv_width, canv_height
    
    def clear(self):
        """ Remove element from canvas """
        self.canvas.delete(self.image)
        self.canvas.delete(self.edge)
        self.canvas.delete(self.marker)