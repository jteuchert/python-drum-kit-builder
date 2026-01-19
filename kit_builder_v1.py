"""
Drum kit builder
Python based program code for designing virtual drum sets.
For hints and explanation of customization see the readme file.

Made by jt 2024-2026
"""

""" Imports """
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import csv
import ast

# Modules
import config
from models.instrument import Instrument
from utils import csv_io
from utils import image_utils
from utils import geometry


ctk.set_appearance_mode("system")

""" Window Creation """
root = tk.Tk()
root.title('Kit Builder')
root.geometry(str(config.WINDOW_SIZE[0]) + 'x' + str(config.WINDOW_SIZE[1]))
#root.state('zoomed')
root.resizable(width=False, height=False)

""" Parameters, Variables """
# Canvas Size
w = int(.5*config.WINDOW_SIZE[0])
h = int(.5*config.WINDOW_SIZE[1])


instruments = [] # index is the instrument ID
elements = {} # dictionary of elements, key is layer
hovering = 0 # layer of element, above which mouse is hovering, 0 if None
selected = 0 # selected layer, 0 if None
all_selected = False # If all elements are selected via all_button

save_path = None

my_canvas = None
rot_slider = None

arr_step = config.ARR_STEP_DEFAULT


# Window icon, does generally not work with .ico on Ubuntu
if not config.ON_LINUX:
    root.iconbitmap(config.RESOURCES_DIR / "Gui" / "8_zultan.ico")

# Background images
background_image = Image.open(config.RESOURCES_DIR / "Environment" / "floor.jpg")
background_image = ImageTk.PhotoImage(background_image)

none_image = Image.open(config.RESOURCES_DIR / "Environment" / "none.png")
none_image = ImageTk.PhotoImage(none_image)


""" Canvas element class """
class Element():
    """ All Elements on self.canvas """
    
    def __init__(self, id, layer, pos=None, rot=0, flipped=False):
        self.instr = instruments[id]
        self.layer = layer
        if pos is None:
            pos = config.SPAWN_POINT.copy()
        self.pos = pos
        
        self.rot = rot
        self.flipped = flipped
        self.r = 4.95*self.instr.size
        
        self.drag_data_x = 0
        self.drag_data_y = 0
        
        # Image, edge and marker
        self.texture = image_utils.instrument_image(self.instr.default_path, 0)
        self.image = my_canvas.create_image(self.pos[0], 
                                            self.pos[1], anchor='center', image=self.texture)
        if self.instr.is_circular:
            if config.ON_LINUX:
                self.edge = my_canvas.create_oval(self.pos[0]-self.r, 
                                                  self.pos[1]-self.r, 
                                                  self.pos[0]+self.r, 
                                                  self.pos[1]+self.r, fill='gray', stipple=config.TRANSPARENT_STIPPLE, width=3, outline='')
                
                self.marker = my_canvas.create_oval(self.pos[0]-self.r, 
                                                    self.pos[1]-self.r, 
                                                    self.pos[0]+self.r, 
                                                    self.pos[1]+self.r, fill='gray', stipple=config.TRANSPARENT_STIPPLE, width=3, outline='')
            else:
                self.edge = my_canvas.create_oval(self.pos[0]-self.r, 
                                                  self.pos[1]-self.r, 
                                                  self.pos[0]+self.r, 
                                                  self.pos[1]+self.r, fill='', width=3, outline='')
                
                self.marker = my_canvas.create_oval(self.pos[0]-self.r, 
                                                    self.pos[1]-self.r, 
                                                    self.pos[0]+self.r, 
                                                    self.pos[1]+self.r, fill='', width=3, outline='')
        else:
            self.polygon_points = [-self.r, 
                                   -self.r, 
                                   -self.r, 
                                   +self.r, 
                                   +self.r, 
                                   +self.r, 
                                   +self.r, 
                                   -self.r] # center at (0, 0)
            if config.ON_LINUX:
                self.edge = my_canvas.create_polygon(self.polygon_points, fill='gray', stipple=config.TRANSPARENT_STIPPLE, width=3, outline='')
                self.marker = my_canvas.create_polygon(self.polygon_points, fill='gray', stipple=config.TRANSPARENT_STIPPLE, width=3, outline='')
            else:
                self.edge = my_canvas.create_polygon(self.polygon_points, fill='', width=3, outline='')
                self.marker = my_canvas.create_polygon(self.polygon_points, fill='', width=3, outline='')
            my_canvas.move(self.edge, self.pos[0], self.pos[1])    
            my_canvas.move(self.marker, self.pos[0], self.pos[1])

        # select self
        global selected
        selected = self.layer
        self.is_selected = True
        my_canvas.itemconfig(self.edge, outline='red')
        
        # canvas binds
        my_canvas.tag_bind(self.marker, "<Enter>", self.highlight)
        my_canvas.tag_bind(self.marker, "<Leave>", self.dehighlight)
        my_canvas.tag_bind(self.marker, "<ButtonPress-1>", self.drag_start)
        my_canvas.tag_bind(self.marker, "<ButtonRelease-1>", self.drag_stop)
        my_canvas.tag_bind(self.marker, "<B1-Motion>", self.drag)


    # Drag functions
    def drag_start(self, e):
        """ Begining drag of an element """
        # record the item and its location
        self.drag_data_x = e.x
        self.drag_data_y = e.y

    def drag_stop(self, e):
        """ End drag of an element """
        # reset the drag information
        self.drag_data_x = 0
        self.drag_data_y = 0

    def drag(self, e):
        """ Handle dragging of an element """
        # compute how much the mouse has moved
        delta_x = e.x - self.drag_data_x
        delta_y = e.y - self.drag_data_y
        
        # move the object
        self.move(delta_x, delta_y)
        
        # record the new position
        self.drag_data_x = e.x
        self.drag_data_y = e.y
                
    # Move
    def move(self, delta_x, delta_y):
        """ Move element on self.canvas """
        x_border = my_canvas.winfo_width()
        y_border = my_canvas.winfo_height()
        if self.pos[0] + delta_x <= 0 or self.pos[0] + delta_x >= x_border:
            delta_x = 0
        if self.pos[1] + delta_y <= 0 or self.pos[1] + delta_y >= y_border:
            delta_y = 0

        my_canvas.move(self.marker, delta_x, delta_y)
        my_canvas.move(self.edge, delta_x, delta_y)
        my_canvas.move(self.image, delta_x, delta_y)
        self.pos[0] += delta_x
        self.pos[1] += delta_y
        
    # Flip
    def flip(self):
        """ Flip image """
        if self.instr.flippable:
            self.flipped = not self.flipped
            if self.flipped:
                self.texture = image_utils.instrument_image(self.instr.flipped_path, self.rot)
            else:
                self.texture = image_utils.instrument_image(self.instr.default_path, self.rot)
            my_canvas.itemconfig(self.image, image=self.texture)

    # Rotate
    def rotate(self, angle):
        """ Rotate image """
        if self.flipped:
            self.texture = image_utils.instrument_image(self.instr.flipped_path, angle)
        else:
            self.texture = image_utils.instrument_image(self.instr.default_path, angle)

        my_canvas.itemconfig(self.image, image=self.texture)
        self.rot = angle
        # Rotate marker shape if rectangular
        if not self.instr.is_circular:
            position = self.pos
            new_points = []
            for i in range(0, 8, 2):
                x, y = self.polygon_points[i], self.polygon_points[i+1]
                rotated = geometry.rotate_point(x, y, angle)
                new_points.append(rotated[0] + position[0])
                new_points.append(rotated[1] + position[1])
            my_canvas.coords(self.edge, new_points)
            my_canvas.coords(self.marker, new_points)

    # Highlight (these functions are only used in the context of mouse binds! 
    # For (de-)highlighting in other cases my_canvas.itemconfig(self.edge, outline=''/'red') is used.)
    def highlight(self, e):
        """ Highlighting an element when mouse is over """
        global hovering
        hovering = self.layer
        my_canvas.itemconfig(self.edge, outline='red')

    # De-highlight
    def dehighlight(self, e):
        """ Undoing highlighting of an element when mouse is not over """
        global selected, hovering, all_selected
        if not all_selected: # prevent dehighlighting if all are selected
            hovering = 0
            if selected != self.layer:
                my_canvas.itemconfig(self.edge, outline='')

    # Mouse click
    def click(self):
        """ Changing elements' state of being selected (T/F) when mouse is clicked on self.canvas """
        global hovering, selected
        if hovering == self.layer:
            self.is_selected = True
            selected = self.layer
            rot_slider.set(-self.rot)
            my_canvas.itemconfig(self.edge, outline='red')
        else:
            self.is_selected = False
            my_canvas.itemconfig(self.edge, outline='')

    # Clear images on self.canvas
    def clear(self):
        """ Remove element from self.canvas """
        my_canvas.delete(self.image)
        my_canvas.delete(self.edge)
        my_canvas.delete(self.marker)



""" Global functions """
def global_click(e):
    """Mouse click handler"""
    global all_selected, selected
    all_selected = False

    for key in elements:
        elements[key].click()
    
    # Update selected
    selected = 0
    for key in elements:
        if elements[key].is_selected:
            selected = key
            activate_flip()
            update_listbox() # this and next line needed?
            return
    if selected == 0:
        deactivate_flip()
    update_listbox()
    
def activate_flip():
    """ Enable flip checkbutton """
    flip_checkbutton.configure(state='normal')
    state = elements[selected].flipped
    if state:
        flip_checkbutton.select()
    else:
        flip_checkbutton.deselect()
        
def deactivate_flip():
    """ Disable flip checkbutton """
    flip_checkbutton.configure(state='disabled')
    flip_checkbutton.deselect()
        
def update_listbox():
    """ Update contents of used gear listbox """
    listbox.delete('0','end')
    for key in elements:
        listbox.insert(0, elements[key].instr.name)
    listbox.selection_clear('0','end')
    if selected > 0:
        last = len(elements)
        listbox.select_set(last - selected)

def listbox_select(e):
    """ Selecting an element in from the listbox """
    global all_selected, selected
    all_selected = False

    w = e.widget
    if len(w.curselection()) > 0:
        idx = int(w.curselection()[0])
        value = w.get(idx)

        selected = 0
        for key in elements:
            elements[key].is_selected = False
            my_canvas.itemconfig(elements[key].edge, outline='')
            if elements[key].instr.name == value:
                selected = key
                elements[key].is_selected = True
                rot_slider.set(-elements[key].rot)
                my_canvas.itemconfig(elements[key].edge, outline='red')
                activate_flip()
                
def slider_callback(angle):
    """ Callback function if slider is used """
    if selected > 0:
        elements[selected].rotate(-int(angle))

def flip_callback():
    """ Callback function if flip checkbox is used """
    elements[selected].flip()


""" Canvas Functions """
# Layer functions
def up_callback():
    """ Move selected element one layer up """
    global selected
    l = selected
    if l < len(elements) and l > 0:
        # Change layer
        swap_up(l)
        selected = l+1
        activate_flip()
        update_listbox()
        
def down_callback():
    """ Move selected element one layer down """
    global selected
    l = selected
    if l > 1:
        # Change layer
        swap_up(l-1)
        selected = l-1
        activate_flip()
        update_listbox()

def swap_up(l):
    """ Swap element with element one layer up """
    my_canvas.tag_raise(elements[l].image, elements[l+1].edge)
    my_canvas.tag_raise(elements[l].edge, elements[l].image)

    # Update instance layers
    elements[l].layer = l+1
    elements[l+1].layer = l
    
    # Swap order
    tmp = elements[l]
    elements[l] = elements[l+1]
    elements[l+1] = tmp
    
    # Update markers
    raise_all_markers()

def top_callback():
    """ Move selected element to highest layer """
    l = selected
    highest_layer = len(elements)
    for _ in range(l, highest_layer):
        up_callback()

def bottom_callback():
    """ Move selected element to lowest layer """
    for _ in range(1, selected):
        down_callback()

    
def add_callback():
    """ Callback function for add button """
    global all_selected, selected, hovering
    selection = gear_tree.selection()
    selection_name = gear_tree.item(selection, option="text")
    if selection_name != "":
        all_selected = False

        # Deselect others
        for key in elements:
            elements[key].click()
            my_canvas.itemconfig(elements[key].edge, outline='')
            elements[key].is_selected = False

        
        new_layer = len(elements) + 1
        for idx, instance in enumerate(instruments):
            if instance.name == selection_name:
                elements[new_layer] = Element(idx, new_layer)
        
                # Add name to listbox
                update_listbox()
        
                # Make sure all markers are on top
                raise_all_markers()
                selected = new_layer
                instr_index = elements[selected].instr.ID
                instruments[instr_index].is_used = True
                update_tree()
                activate_flip()
                break
    
def remove_callback():
    """ Remove the (if any) currently selected element """
    global selected
    if selected > 0:
        # Gear tree stuff
        instr_index = elements[selected].instr.ID
        instruments[instr_index].is_used = False

        old_length = len(elements)
        elements[selected].clear()
        del elements[selected]

        # Reorder layering
        # Iterate through elements, stopping before reaching the old dict length (new_length = old_length - 1)
        for i in range(selected, old_length):
            elements[i] = elements.pop(i+1)
            elements[i].layer = i

        selected = 0

        # Update listbox and gear tree
        update_listbox()
        update_tree()

        deactivate_flip()
        
        
def update_tree():   
    """ Update gear tree """
    # Delete each child item
    child_items = gear_tree.get_children(drums_id)
    for child in child_items:
        gear_tree.delete(child)
    child_items = gear_tree.get_children(cymbals_id)
    for child in child_items:
        gear_tree.delete(child)
    child_items = gear_tree.get_children(other_id)
    for child in child_items:
        gear_tree.delete(child)

    # Repopulate tree
    for inst in instruments:
        if inst.type == "drum" and not inst.is_used:
            gear_tree.insert(drums_id, tk.END, text=inst.name)
        if inst.type == "cymbal" and not inst.is_used:
            gear_tree.insert(cymbals_id, tk.END, text=inst.name)
        if inst.type == "other" and not inst.is_used:
            gear_tree.insert(other_id, tk.END, text=inst.name)
    
    
def raise_all_markers():
    """ Move up all markers in order to ensure correct selectability """
    for key in elements:
        my_canvas.tag_raise(elements[key].marker)


""" Save, Load """
def save_as():
    global save_path
    # Open file dialog for saving file
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialdir=config.KITS_DIR)
        
    if file_path:
        csv_io.save_to_csv(file_path, config.COLUMN_NAMES)
        save_path = file_path
        save()
        root.title(file_path)
        #save_label.config(text="Save path: " + file_path)
    

def save():
    if save_path is not None:
        # clear file
        with open(save_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(config.COLUMN_NAMES)
        
        # Save to file
        for key in elements:
            new_element = {"ID": elements[key].instr.ID, 
                           "layer": elements[key].layer, 
                           "position": elements[key].pos, 
                           "rotation": elements[key].rot, 
                           "flipped": int(elements[key].flipped)}
            csv_io.append_to_csv(save_path, new_element, config.COLUMN_NAMES)
        print("Data saved to:", save_path)
        messagebox.showinfo("Saved", "Kit saved successfully.")
    else:
        save_as()


def load():
    global selected, save_path
    # Open file dialog for loading file
    file_path = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        reset()
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            new_layer = 1
            for row in reader:
                elements[new_layer] = Element(int(row["ID"]), 
                                              int(row["layer"]), 
                                              ast.literal_eval(row["position"]), 
                                              int(row["rotation"]), 
                                              bool(int(row["flipped"])))
                elements[new_layer].rotate(int(row["rotation"]))
                instruments[int(row["ID"])].is_used = True
                new_layer += 1
        
        # Make sure all markers are on top
        raise_all_markers()
        
        # Deselect all elements
        for key in elements:
            my_canvas.itemconfig(elements[key].edge, outline='')
            elements[key].is_selected = False
        selected = 0
        update_listbox()
        update_tree()

        save_path = file_path
        root.title(file_path)
            
        
def reset():
    """ Reset function """
    global elements, hovering, selected, all_selected, save_path
    for key in elements:
        elements[key].clear()
        
    for i in range(1, len(elements)+1):
        del elements[i]
    
    # Reset all parameters (selected, elements...)
    elements = {}
    hovering = 0
    selected = 0
    all_selected = False
    save_path = None

    # Reset tree and listbox
    for inst in instruments:
        # Set all instruments to not used
        inst.is_used = False
    update_tree()
    listbox.delete('0','end')

    rot_slider.set(0)
    deactivate_flip()
    
    #save_label.config(text="")
    root.title('Set Constructor')
    
    
def bg_callback(e):
    """ Callback function if background image is changed """
    value = bg_box.get()
    if value == 'wood floor 1':
        my_canvas.itemconfig(bg, image=background_image)
    if value == 'none':
        my_canvas.itemconfig(bg, image=none_image)



def get_real_canvas_size():
    # Ensure the layout is updated
    root.update_idletasks()
    # Get the real size of the canvas
    return (my_canvas.winfo_width(), my_canvas.winfo_height())



def save_image(elements, output_path):
    """ Function to save canvas as image (without edges, buttons) """
    # Create a new blank image using Pillow
    image = Image.new("RGBA", get_real_canvas_size(), (255, 255, 255, 0))  # Transparent background

    # Background, needs fix (position, scale, different bgs)
    bg_img = Image.open(config.RESOURCES_DIR / "Environment" / "floor.jpg")
    image.paste(bg_img, (0, 0))
    
    # Iterate over the image items
    for key in elements:
        # Get the image's position and the PIL image object
        coords = elements[key].pos
        if elements[key].flipped:
            image_path = elements[key].instr.flipped_path
        else:
            image_path = elements[key].instr.default_path
        
        pillow_image = Image.open(image_path)
        pillow_image_rot = pillow_image.rotate(elements[key].rot, resample=Image.BICUBIC, expand=True)            
        
        # Adjust anchors: on canvas, anchor is center. for the pillow image it is the top-left corner
        image_width, image_height = pillow_image_rot.size
        x, y = int(coords[0]) - image_width // 2, int(coords[1]) - image_height // 2

        # Paste the image onto the blank image
        image.paste(pillow_image_rot, (x, y), pillow_image_rot)

    # Save the final image
    image.save(output_path)
    

def save_image_as():
    # Open file dialog for saving file
    file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                             filetypes=[("PNG files", "*.png")], 
                                             initialdir=config.KITS_DIR
                                             )
    
    if file_path:
        save_image(elements, file_path)

    

""" Window Layout """
# Grid
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=40)
root.grid_columnconfigure(4, weight=40)
root.grid_columnconfigure(5, weight=40)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=30)
root.grid_rowconfigure(6, weight=1)
root.grid_rowconfigure(7, weight=50)
root.grid_rowconfigure(8, weight=1)
root.grid_rowconfigure(9, weight=1)


PAD = 10

# Pool Label
tk.Label(root, text= "Instruments pool").grid(column=0, row=0, sticky='nswe')

# Save file path Label
#save_label = tk.Label(root, text= "Save path: None", wraplength=500, height=1)
#save_label.grid(column=3, row=0, columnspan=3, sticky='nsw', padx=10)

# Canvas
cv_scrollbar_frame = tk.Frame(root)
cv_scrollbar_frame.grid(column=3, row=1, rowspan=7, columnspan=3, sticky='nswe', padx=PAD)

my_canvas = tk.Canvas(cv_scrollbar_frame, highlightbackground="gray", highlightthickness=2, width=w, height=h, scrollregion=(0,0,1200,700), bg="white")
#my_canvas.grid(column=3, row=1, rowspan=7, columnspan=3, sticky='nswe', padx=PAD)

# Add vertical scrollbar
#v_scrollbar = tk.Scrollbar(cv_scrollbar_frame, orient="vertical", command=my_canvas.yview)
#v_scrollbar.pack(side="right", fill="y")

# Add horizontal scrollbar
#h_scrollbar = tk.Scrollbar(cv_scrollbar_frame, orient="horizontal", command=my_canvas.xview)
#h_scrollbar.pack(side="bottom", fill="x")

my_canvas.config(width=w, height=h)
my_canvas.pack(side="left", expand=True, fill="both")

# Canvas scrollbars usage config
#my_canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)


# Background
bg = my_canvas.create_image(200, 0, anchor='center', image=background_image)

# Bind mouse left-click on canvas
my_canvas.bind("<Button->", global_click)

# Bind arrow keys
def left(e):
    delta_x = -arr_step
    delta_y = 0
    if all_selected:
        min_x_key = min(elements, key=lambda k: elements[k].pos[0])
        min_x = elements[min_x_key].pos[0]
        if min_x + delta_x > 0:
            for key in elements:
                elements[key].move(delta_x, delta_y)
    elif selected > 0:
        elements[selected].move(delta_x, delta_y)

def right(e):
    delta_x = arr_step
    delta_y = 0
    if all_selected:
        x_border = my_canvas.winfo_width()
        max_x_key = max(elements, key=lambda k: elements[k].pos[0])
        max_x = elements[max_x_key].pos[0]
        if max_x + delta_x < x_border:
            for key in elements:
                elements[key].move(delta_x, delta_y)
    elif selected > 0:
        elements[selected].move(delta_x, delta_y)

def up(e):
    delta_x = 0
    delta_y = -arr_step
    if all_selected:
        min_y_key = min(elements, key=lambda k: elements[k].pos[1])
        min_y = elements[min_y_key].pos[1]
        if min_y + delta_y > 0:
            for key in elements:
                elements[key].move(delta_x, delta_y)
    elif selected > 0:
        elements[selected].move(delta_x, delta_y)

def down(e):
    delta_x = 0
    delta_y = arr_step
    if all_selected:
        y_border = my_canvas.winfo_height()
        max_y_key = max(elements, key=lambda k: elements[k].pos[1])
        max_y = elements[max_y_key].pos[1]
        if max_y + delta_y < y_border:
            for key in elements:
                elements[key].move(delta_x, delta_y)
    elif selected > 0:
        elements[selected].move(delta_x, delta_y)

# Bind the move function
root.bind("<Left>", left)
root.bind("<Right>", right)
root.bind("<Up>", up)
root.bind("<Down>", down)

# Layer Buttons
arrow_top_pil = Image.open(config.RESOURCES_DIR / 'Gui' / 'arrow_top.png').resize((21, 21))
arrow_top = ImageTk.PhotoImage(arrow_top_pil)

arrow_up_pil = Image.open(config.RESOURCES_DIR / 'Gui' / 'arrow_up.png').resize((21, 21))
arrow_up = ImageTk.PhotoImage(arrow_up_pil)

arrow_down_pil = Image.open(config.RESOURCES_DIR / 'Gui' / 'arrow_down.png').resize((21, 21))
arrow_down = ImageTk.PhotoImage(arrow_down_pil)

arrow_bottom_pil = Image.open(config.RESOURCES_DIR / 'Gui' / 'arrow_bottom.png').resize((21, 21))
arrow_bottom = ImageTk.PhotoImage(arrow_bottom_pil)

top_button= tk.Button(root, image=arrow_top, borderwidth=0, highlightthickness=0, command=top_callback)
top_button.grid(column=3, row=1, sticky='w', padx=PAD+5, pady=2)

up_button = tk.Button(root, image=arrow_up, borderwidth=0, highlightthickness=0, command=up_callback)
up_button.grid(column=3, row=2, sticky='w', padx=PAD+5, pady=2)

down_button = tk.Button(root, image=arrow_down, borderwidth=0, highlightthickness=0, command=down_callback)
down_button.grid(column=3, row=3, sticky='w', padx=PAD+5, pady=2)

bottom_button = tk.Button(root, image=arrow_bottom, borderwidth=0, highlightthickness=0, command=bottom_callback)
bottom_button.grid(column=3, row=4, sticky='w', padx=PAD+5, pady=2)

# Pool Tree
tree_frame = tk.Frame(root)
tree_scrollbar = tk.Scrollbar(tree_frame)
tree_scrollbar.pack(side='right', fill='y')
gear_tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
gear_tree.pack(fill='both', expand=True)

gear_tree.config(yscrollcommand=tree_scrollbar.set)
tree_scrollbar.config(command=gear_tree.yview)
tree_frame.grid(column=0, row=1, columnspan=2, rowspan=5, sticky='nswe', padx=PAD)

# Add parent items with icons
drums_icon = tk.PhotoImage(file=config.RESOURCES_DIR / 'Gui' / 'drums_icon.png')
cymbals_icon = tk.PhotoImage(file=config.RESOURCES_DIR / 'Gui' / 'cymbals_icon.png')
other_icon = tk.PhotoImage(file=config.RESOURCES_DIR / 'Gui' / 'other_icon.png')
drums_id = gear_tree.insert("", tk.END, text=" Drums", image=drums_icon)
cymbals_id = gear_tree.insert("", tk.END, text=" Cymbals", image=cymbals_icon)
other_id = gear_tree.insert("", tk.END, text=" Other", image=other_icon)

# Add Button
add_button = tk.Button(root, text ="add", command=add_callback)
add_button.grid(column=0, row=6, sticky='nswe', padx=2*PAD, pady=PAD)

# Remove Button
remove_button = tk.Button(root, text="remove", command= remove_callback)
remove_button.grid(column=1, row=6, sticky='nswe', padx=2*PAD, pady=PAD)

# Used Elements Listbox
listbox_frame = tk.Frame(root)
listbox_scrollbar = tk.Scrollbar(listbox_frame)
listbox_scrollbar.pack(side='right', fill='y')
listbox = tk.Listbox(listbox_frame, exportselection=False)
listbox.pack(fill='both', expand=True)

listbox.config(yscrollcommand=listbox_scrollbar.set)
listbox_scrollbar.config(command=listbox.yview)
listbox_frame.grid(column=0, row=7, columnspan=2, sticky='nswe', padx=PAD+1)
listbox.bind('<<ListboxSelect>>', listbox_select)

# Disable key selection for listbox
def listbox_up(e):
    up([])
    return "break"

def listbox_down(e):
    down([])
    return "break"

listbox.bind("<Up>", listbox_up)
listbox.bind("<Down>", listbox_down)

# Background selection
#bg_label = tk.Label(root, text= "Background:")
#bg_label.grid(column=4, row=0, sticky='nsw', padx=10)

n = tk.StringVar() 
bg_box = ttk.Combobox(root, width = 27, textvariable=n, state='readonly') 
bg_box['values'] = ('wood floor 1', 'none')
bg_box.current(0)
bg_box.grid(column = 5, row = 0, sticky='e', padx=PAD)

bg_box.bind('<<ComboboxSelected>>', bg_callback)


def gear_popup():
    """ Gear Pop-up """
    # Make pop-up window
    top = tk.Toplevel(root)
    top.geometry("550x350")
    top.geometry("+300+300")
    top.title("Gear")

    # Window settings
    top.attributes('-topmost', 1)
    top.grab_set()
    
    # Grid
    top.grid_columnconfigure(0, weight=1)
    top.grid_rowconfigure(0, weight=1)
    
    # Gear Listbox
    gear_frame = tk.Frame(top)
    gear_scrollbar = tk.Scrollbar(gear_frame)
    gear_scrollbar.pack(side='right', fill='y')
    gear_lb = tk.Listbox(gear_frame)
    gear_lb.pack(fill='both', expand=True)
    for inst in instruments:
        string = str(inst.ID) + "      " + inst.name
        gear_lb.insert('end', string)
        
    gear_lb.config(yscrollcommand=gear_scrollbar.set)
    gear_scrollbar.config(command=gear_lb.yview)
    gear_frame.grid(column=0, row=0, sticky='nswe')
    

def gearlist_popup():
    """ Gearlist Pop-up """
    # Make pop-up window
    top = tk.Toplevel(root)
    top.geometry("550x350")
    top.geometry("+300+300")
    top.title("Gear")

    # Window settings
    top.attributes('-topmost', 1)
    top.grab_set()
    
    # Grid
    top.grid_columnconfigure(0, weight=1)
    top.grid_rowconfigure(0, weight=1)
    
    # Gear Listbox
    gear_frame = tk.Frame(top)
    gear_scrollbar = tk.Scrollbar(gear_frame)
    gear_scrollbar.pack(side='right', fill='y')
    gear_lb = tk.Listbox(gear_frame)
    gear_lb.pack(fill='both', expand=True)
    for key in elements:
        string = str(elements[key].instr.ID) + "    " + elements[key].instr.name
        gear_lb.insert('end', string)
        
    gear_lb.config(yscrollcommand=gear_scrollbar.set)
    gear_scrollbar.config(command=gear_lb.yview)
    gear_frame.grid(column=0, row=0, sticky='nswe')
    
    
def exit_popup():
    """ Exit Pop-up """
    # Make pop-up window
    top = tk.Toplevel(root)
    top.geometry("200x120")
    top.geometry("+300+300")
    top.title("Exit")

    # Window settings
    top.attributes('-topmost', 1)
    top.grab_set()
    
    # Grid
    top.grid_columnconfigure(0, weight=1)
    top.grid_columnconfigure(1, weight=1)
    top.grid_rowconfigure(0, weight=1)
    top.grid_rowconfigure(1, weight=2)
    
    tk.Label(top, text= "Are you sure you want to exit?").grid(column=0, row=0, columnspan=2, sticky='nswe', pady=10)
    tk.Button(top, text="Yes", command=root.destroy).grid(column=0, row=1, sticky='nswe', padx=10, pady=20)
    tk.Button(top, text="No", command=lambda: close_top(top)).grid(column=1, row=1, sticky='nswe', padx=10, pady=20)
    

def new_popup():
    """ New Pop-up """
    # Make pop-up window
    top = tk.Toplevel(root)
    top.geometry("200x120")
    top.geometry("+300+300")
    top.title("New")

    # Window settings
    top.attributes('-topmost', 1)
    top.grab_set()
    
    # Grid
    top.grid_columnconfigure(0, weight=1)
    top.grid_columnconfigure(1, weight=1)
    top.grid_rowconfigure(0, weight=1)
    top.grid_rowconfigure(1, weight=2)
    
    tk.Label(top, text= "Are you sure you want to reset?").grid(column=0, row=0, columnspan=2, sticky='nswe', pady=10)
    tk.Button(top, text="Yes", command=lambda: close_top_reset(top)).grid(column=0, row=1, sticky='nswe', padx=10, pady=20)
    tk.Button(top, text="No", command=lambda: close_top(top)).grid(column=1, row=1, sticky='nswe', padx=10, pady=20)

    
def close_top(top):
    top.destroy()
    
def close_top_reset(top):
    reset()
    top.destroy()
    
def arr_step_dec():
    """ Decrease arrow key movement step """
    global arr_step
    if arr_step > 3:
        arr_step -= 3
    
def arr_step_inc():
    """ Increase arrow key movement step """
    global arr_step
    if arr_step < 20:
        arr_step += 3


def all_callback():
    """ Callback function for select all button """
    global all_selected, selected
    if all_selected:
        all_selected = False
        selected = 0
        for key in elements:
            my_canvas.itemconfig(elements[key].edge, outline='')
            elements[key].is_selected = False
    else:
        selected = 0
        for key in elements:
            my_canvas.itemconfig(elements[key].edge, outline='red')
        all_selected = True


all_button = tk.Button(root, text="Select all", command= all_callback)
all_button.grid(column=0, row=8, sticky='nswe', padx=PAD, pady=PAD)

# Rotation Slider
rot_slider = tk.Scale(root, from_=-179, to=179, orient='horizontal', command=slider_callback)
rot_slider.grid(column=4, row=8, columnspan=2, sticky='nswe', padx=50)

# Flip Checkbutton
flip_checkbutton = tk.Checkbutton(root, text='Flip cymbal', command=flip_callback, state='disabled')
flip_checkbutton.grid(column=3, row=8)

# Menu bar
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=new_popup)
filemenu.add_command(label="Load...", command=load)
filemenu.add_command(label="Save", command=save)
filemenu.add_command(label="Save as...", command=save_as)
filemenu.add_command(label="Save image as...", command=save_image_as)


#filemenu.add_command(label="Print gear list...", command=gearlist_popup)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=exit_popup)
menubar.add_cascade(label="File", menu=filemenu)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="View gear", command=gear_popup)
helpmenu.add_command(label="Increase move step (arrows)", command=arr_step_inc)
helpmenu.add_command(label="Decrease move step (arrows)", command=arr_step_dec)
#helpmenu.add_command(label="Background...") #drop down menu? under canvas or menu bar?
menubar.add_cascade(label="Edit", menu=helpmenu) # ask for save before...

root.config(menu=menubar)

    
# Append two rows to the CSV file for testing
#new_element = {"name": "Crash", "type": "cymbal", "is_circular": 1, "size": 22, "flippable": 1, "default_path": config.RESOURCES_DIR / "Cymbals" / "22_crash.png", "flipped_path": config.RESOURCES_DIR / "Cymbals" / "22_crash_f.png"}
#append_to_csv(config.GEAR_FILE, new_element)
#new_element = {"name": "Bell", "type": "cymbal", "is_circular": 1, "size": 8, "flippable": 1, "default_path": config.RESOURCES_DIR / "Cymbals" / "8_bell.png", "flipped_path": config.RESOURCES_DIR / "Cymbals" / "8_bell_f.png"}
#append_to_csv(config.GEAR_FILE, new_element)
# ["name", "type", "is_circular", "size", "flippable", "default_path", "flipped_path"]

def write_gear_file():
    """ (Re-)write the gear.csv file from GEAR_LIST """
    if True: # Writes the gear.csv file newly every time the code is executed (for accurate image paths), might optimize in the future
        # File does not exists
        with open(config.GEAR_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=config.COLUMN_NAMES_GEAR)
            writer.writeheader()
    
    for k in config.GEAR_LIST:
        new_element = {"name": k[0], "type": k[1], "is_circular": k[2], "size": k[3], "flippable": k[4], "default_path": k[5], "flipped_path": k[6]}
        with open(config.GEAR_FILE, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=config.COLUMN_NAMES_GEAR)
            writer.writerow(new_element)
    

# (Re-)write the gear.csv file
write_gear_file()
   

# Create Instrument instances
row_count = 0
with open(config.GEAR_FILE, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        instruments.append(Instrument(row_count))
        row_count += 1
        
update_tree()

# "Are you sure?" pop up for closing
root.protocol('WM_DELETE_WINDOW', exit_popup)

root.mainloop()