"""
Drum kit builder
Python based program code for designing virtual drum sets.
For hints and explanation of customization see the readme file.

Made by jt 2024
"""

""" Imports """
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import csv
from pathlib import Path
import math
import ast
from sys import platform

# On Linux and Windows the code needs to differ because on Linux fill='' does not give a transparent shape (for marker and edge). Here it is drawn using an xbm file instead.
# Only tested on Ubuntu 22.04.3 LTS and Windows 10/11
on_linux = False
if platform == "linux" or platform == "linux2":
    on_linux = True # True if on linux

window_size = [1200, 700]

ctk.set_appearance_mode("system")

""" Window Creation """
root = tk.Tk()
root.title('Kit Builder')
root.geometry(str(window_size[0]) + 'x' + str(window_size[1]))
#root.state('zoomed')
root.resizable(width=False, height=False)

""" Parameters, Variables """
# Canvas Size
w = int(.5*window_size[0])
h = int(.5*window_size[1])
arr_step = 1 # move step when using arrow keys

instruments = [] # index = instr. ID
elements = dict() # dictionary of elements, key is layer
hovering = 0 # layer of element, above which mouse is hovering, 0 if None
selected = 0 # selected layer, 0 if None
all_selected = False # If all elements are selected via all_button

column_names_gear = ["name", "type", "is_circular", "size", "flippable", "default_path", "flipped_path"] # for gear pool creation
column_names = ["ID", "layer", "position", "rotation", "flipped"] # for loading/saving

# Directory paths
base_dir = os.getcwd() # base Directory
base_dir = Path(base_dir)
resources_dir = base_dir / "resources"
gear_file = resources_dir / "gear.csv"
kits_dir = base_dir / "Kits"

#root.iconbitmap(resources_dir / "Gui" / "8_zultan.ico")

save_path = None

background_image = Image.open(resources_dir / "Environment" / "floor.jpg")
#background_image = background_image.resize((background_image.width // 4, background_image.height // 4))
background_image = ImageTk.PhotoImage(background_image)

none_image = Image.open(resources_dir / "Environment" / "none.png")
#background_image = background_image.resize((background_image.width // 4, background_image.height // 4))
none_image = ImageTk.PhotoImage(none_image)


""" Classes """
class Instrument:
    """ All gear, each element with its properties """
    def __init__(self, idx):
        row = get_row_from_csv(gear_file, idx)
        self.is_used = False
        self.ID = idx        
        self.name = row["name"]
        self.type = row["type"]
        self.is_circular = row["is_circular"] == "1"
        self.size = int(row["size"])
        self.flippable = row["flippable"] == "1"
        self.default_path = resources_dir / row["default_path"]
        self.flipped_path = resources_dir / row["flipped_path"]

class Element():
    """ All Elements on canvas """
    spawn_point = [50, 50]
    
    def __init__(self, ID, layer, pos=None, rot=0, flipped=False):
        self.instr = instruments[ID]
        self.layer = layer
        if pos is None:
            pos = Element.spawn_point.copy()
        self.pos = pos
        
        self.rot = rot
        self.flipped = flipped
        self.r = 4.95*self.instr.size
        
        self.drag_data_x = 0
        self.drag_data_y = 0
        
        # Image, edge and marker
        self.texture = instrument_image(self.instr.default_path, 0)
        self.image = my_canvas.create_image(self.pos[0], 
                                            self.pos[1], anchor='center', image=self.texture)
        if self.instr.is_circular:
            if on_linux:
                self.marker = my_canvas.create_oval(self.pos[0]-self.r, 
                                                    self.pos[1]-self.r, 
                                                    self.pos[0]+self.r, 
                                                    self.pos[1]+self.r, fill='gray', stipple='@transparent.xbm', width=3, outline='')
            else:
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
            if on_linux:
                self.marker = my_canvas.create_polygon(self.polygon_points, fill='gray', stipple='@transparent.xbm', width=3, outline='')
            else:
                self.marker = my_canvas.create_polygon(self.polygon_points, fill='', width=3, outline='')
                
            my_canvas.move(self.marker, self.pos[0], self.pos[1])
        
        # select self
        global selected
        selected = self.layer
        self.is_selected = True
        self.highlight([])
        
        # Binds
        my_canvas.tag_bind(self.marker, "<Enter>", self.highlight)
        my_canvas.tag_bind(self.marker, "<Leave>", self.dehighlight) 
        my_canvas.tag_bind(self.marker, "<ButtonPress-1>", self.drag_start)
        my_canvas.tag_bind(self.marker, "<ButtonRelease-1>", self.drag_stop)
        my_canvas.tag_bind(self.marker, "<B1-Motion>", self.drag)
        

    # Drag functions
    def drag_start(self, e):
        """Begining drag of an element"""
        # record the item and its location
        self.drag_data_x = e.x
        self.drag_data_y = e.y

    def drag_stop(self, e):
        """End drag of an element"""
        # reset the drag information
        self.drag_data_x = 0
        self.drag_data_y = 0

    def drag(self, e):
        """Handle dragging of an element"""
        # compute how much the mouse has moved
        delta_x = e.x - self.drag_data_x
        delta_y = e.y - self.drag_data_y
        
        # move the object the appropriate amount
        self.move(delta_x, delta_y)
        
        # record the new position
        self.drag_data_x = e.x
        self.drag_data_y = e.y
                
    # Move
    def move(self, delta_x, delta_y):
        """ Move element on canvas """
        x_border = my_canvas.winfo_width()
        y_border = my_canvas.winfo_height()
        destination_h = self.pos[0] + delta_x
        destination_v = self.pos[1] + delta_y
        if destination_h <= 0:
            delta_x = -self.pos[0] # instead of 0, because arr_step could be > pos
        if destination_h >= x_border:
            delta_x = x_border - self.pos[0]
        if destination_v <= 0:
            delta_y = -self.pos[1]
        if destination_v >= y_border:
            delta_y = y_border - self.pos[1]
            
        my_canvas.move(self.marker, delta_x, delta_y)
        my_canvas.move(self.image, delta_x, delta_y)
        self.pos[0] += delta_x
        self.pos[1] += delta_y
        
    # Flip
    def flip(self):
        """ Flip image """
        if self.instr.flippable:
            self.flipped = not self.flipped
            if self.flipped:
                self.texture = instrument_image(self.instr.flipped_path, self.rot)
            else:
                self.texture = instrument_image(self.instr.default_path, self.rot)
            my_canvas.itemconfig(self.image, image=self.texture)
    
    # rotate
    def rotate(self, angle):
        """ Rotate image """
        #if self.instr.flippable:
        if self.flipped:
            self.texture = instrument_image(self.instr.flipped_path, angle)
        else:
            self.texture = instrument_image(self.instr.default_path, angle)
                
        my_canvas.itemconfig(self.image, image=self.texture)
        self.rot = angle
        if not self.instr.is_circular:
            position = self.pos
            new_points = []
            for i in range(0, 8, 2):
                x, y = self.polygon_points[i], self.polygon_points[i+1]
                rotated = rotate_point(x, y, angle)
                new_points.append(rotated[0] + position[0])
                new_points.append(rotated[1] + position[1])
            my_canvas.coords(self.marker, new_points)
                
    # highlight
    def highlight(self, e):
        """Highlighting an element when mouse is over"""
        global hovering
        hovering = self.layer
        my_canvas.itemconfig(self.marker, outline='red')
    
    # de-highlight
    def dehighlight(self, e):
        """Undoing highlighting of an element when mouse is not over"""
        if not all_selected: # prevent dehighlighting if all are selected
            global hovering
            hovering = 0
            if selected != self.layer:
                my_canvas.itemconfig(self.marker, outline='')
    
    # click
    def click(self):
        """Changing elements' state of being selected (T/F) when mouse is clicked on canvas"""
        global hovering
        global selected
        if hovering == self.layer:
            self.is_selected = True
            selected = self.layer
            rot_slider.set(-self.rot)
            my_canvas.itemconfig(self.marker, outline='red')
        else:
            self.is_selected = False
            my_canvas.itemconfig(self.marker, outline='')
    
    # Clear images on canvas
    def clear(self):
        """ Remove element from canvas """
        my_canvas.delete(self.image)
        my_canvas.delete(self.marker)


""" Functions """
def instrument_image(path, angle):
    """ Create element image, rotated correctly """
    pil_img_resize = Image.open(path)
    #pil_img_resize = pil_img.resize((pil_img.width // 10, pil_img.height // 10))
    pil_image_resize_rotated = pil_img_resize.rotate(angle, resample=Image.BICUBIC, expand=True)
    img = ImageTk.PhotoImage(pil_image_resize_rotated)
    return img

def rotate_point(x, y, angle):
    """ Rotate point, for rotated rectangle """
    # Convert angle from degrees to radians
    angle_rad = math.radians(-angle) # negative for correct rotation direction
    
    # Calculate new coordinates
    new_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    new_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)  
    return new_x, new_y

def global_click(e):
    """Mouse click handler"""
    global all_selected
    all_selected = False
    
    global selected
    for key in elements:
        elements[key].click()
    
    # update selected
    selected = 0
    for key in elements:
        if elements[key].is_selected:
            selected = key # needed?
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
    listbox.delete('0','end')
    for key in elements:
        listbox.insert(0, elements[key].instr.name)
    listbox.selection_clear('0','end')
    if selected > 0:
        last = len(elements)
        listbox.select_set(last - selected)
        
def listbox_select(e):
    global all_selected
    all_selected = False
    
    w = e.widget
    if len(w.curselection()) > 0:
        idx = int(w.curselection()[0])
        value = w.get(idx)
    
        global selected
        for key in elements:
            elements[key].is_selected = False
            my_canvas.itemconfig(elements[key].marker, outline='')
            if elements[key].instr.name == value:
                selected = key    
                elements[key].is_selected = True
                rot_slider.set(-elements[key].rot)
                my_canvas.itemconfig(elements[key].marker, outline='red')
                activate_flip()
                
def sliderCallBack(angle):
    global selected
    if selected > 0:
        elements[selected].rotate(-int(angle))
        
def flip_change():
    elements[selected].flip()
        

""" Canvas Functions """
# Layer functions
def upCallBack():
    """Move selected element one layer up"""
    global selected
    l = selected
    if l < len(elements) and l > 0:
        # Change layer
        swap_up(l)
        selected = l+1
        activate_flip()
        update_listbox()
        
def downCallBack():
    """Move selected element one layer down"""
    global selected
    l = selected
    if l > 1:
        # Change layer
        swap_up(l-1)
        selected = l-1
        activate_flip()
        update_listbox()

def swap_up(l):
    my_canvas.tag_raise(elements[l].image, elements[l+1].marker)
    my_canvas.tag_raise(elements[l].marker, elements[l].image)
    
    # Update instance layers 
    elements[l].layer = l+1
    elements[l+1].layer = l
    
    # Swap order
    tmp = elements[l]
    elements[l] = elements[l+1]
    elements[l+1] = tmp
    
    # Update markers
    raise_all_markers()

def topCallBack():
    """Move selected element to highest layer"""
    global selected
    l = selected
    highest_layer = len(elements)
    for i in range(l, highest_layer):
        upCallBack()

def bottomCallBack():
    """Move selected element to lowest layer"""
    global selected
    for i in range(1, selected):
        downCallBack()

    
def addCallBack():
    #global selected
    #selected = 0
    
    selection = gear_tree.selection()
    selection_name = gear_tree.item(selection, option="text")
    if selection_name != "":
        global all_selected, selected
        all_selected = False
        selected = 0
        
        # Deselect others
        for key in elements:
            elements[key].dehighlight([])
            elements[key].is_selected = False
        
        new_layer = len(elements) + 1
        for i, instance in enumerate(instruments):
            if instance.name == selection_name:
                idx = i
                elements[new_layer] = Element(idx, new_layer)
        
                # Add name to listbox
                update_listbox()
        
                # Make sure all markers are on top
                raise_all_markers()

                instr_index = elements[selected].instr.ID
                instruments[instr_index].is_used = True
                update_tree()
                activate_flip()
                break
    
def removeCallBack():
    """Remove the (if any) currently selected element"""
    global selected    
    if selected > 0:
        # Gear tree stuff
        instr_index = elements[selected].instr.ID
        #instr_type = elements[selected].instr.type
        instruments[instr_index].is_used = False
        
        #deleted_name = elements[selected].instr.name
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
    # Remove all childs
    #for item in gear_tree.get_children(): # used self.tree instead
    #    gear_tree.delete(item)
        
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
    """Move up all markers in order to ensure correct selectability"""
    #for key in elements:
    #    my_canvas.tag_raise(elements[key].marker)

""" Read, Write Data Functions"""
# Function to save data to a CSV file
def save_to_csv(filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=column_names)
        writer.writeheader()


# Function to read data from a CSV file
def read_from_csv(filename):
    data = []
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

# Function to append a row to the CSV file
def append_to_csv(filename, row):
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=column_names)
        writer.writerow(row)

# Function to delete a row from the CSV file based on index
def delete_from_csv(filename, index):
    data = read_from_csv(filename)
    del data[index]
    save_to_csv(filename, data)

# Function to get a row from the CSV file
def get_row_from_csv(filename, row_index):
    data = read_from_csv(filename)
    return data[row_index]
    


""" Save, Load """
def save_as():
    # Open file dialog for saving file
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialdir=kits_dir)
        
    if file_path:
        #with open(file_path, 'w', newline='') as csvfile:
        save_to_csv(file_path)
        global save_path 
        save_path = file_path
        save()
        root.title(file_path)
        #save_label.config(text="Save path: " + file_path)
    

def save():
    if save_path is not None:
        # clear file
        with open(save_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(column_names)
        
        # Save to file
        for key in elements:
            new_element = {"ID": elements[key].instr.ID, 
                           "layer": elements[key].layer, 
                           "position": elements[key].pos, 
                           "rotation": elements[key].rot, 
                           "flipped": int(elements[key].flipped)}
            append_to_csv(save_path, new_element)
        print("Data saved to:", save_path)
        messagebox.showinfo("Saved", "Kit saved successfully.")
    else:
        save_as()


def load():
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
            elements[key].dehighlight([])
            elements[key].is_selected = False
        global selected
        selected = 0
        
        update_listbox()
        update_tree()
        
        global save_path 
        save_path = file_path
        #save_label.config(text="Save path: " + file_path)
        root.title(file_path)
            
        
def reset():
    global elements
    for key in elements:
        elements[key].clear()
        
    for i in range(1, len(elements)+1):
        del elements[i]
    
    # Reset all parameters (selected, elements...)
    global hovering, selected, all_selected, save_path
    elements = dict()
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
    
    
def bgCallBack(e):
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


# Function to save canvas as image (without edges, buttons)
def save_image(elements, output_path):
    # Create a new blank image using Pillow
    image = Image.new("RGBA", get_real_canvas_size(), (255, 255, 255, 0))  # Transparent background

    # Background, needs fix (position, scale, different bgs)
    bg_img = Image.open(resources_dir / "Environment" / "floor.jpg")
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
        
        # Adjust potition: on canvas, anchor is center. for the pillow image it is the top-left corner
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
                                             initialdir=kits_dir
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


pad = 10

# Pool Label
tk.Label(root, text= "Instruments pool").grid(column=0, row=0, sticky='nswe')

# Save file path Label
#save_label = tk.Label(root, text= "Save path: None", wraplength=500, height=1)
#save_label.grid(column=3, row=0, columnspan=3, sticky='nsw', padx=10)

# Canvas
cv_scrollbar_frame = tk.Frame(root)
cv_scrollbar_frame.grid(column=3, row=1, rowspan=7, columnspan=3, sticky='nswe', padx=pad)

my_canvas = tk.Canvas(cv_scrollbar_frame, highlightbackground="gray", highlightthickness=2, width=w, height=h, scrollregion=(0,0,1200,700), bg="white")
#my_canvas.grid(column=3, row=1, rowspan=7, columnspan=3, sticky='nswe', padx=pad)

# Add vertical scrollbar
#v_scrollbar = tk.Scrollbar(cv_scrollbar_frame, orient="vertical", command=my_canvas.yview)
#v_scrollbar.pack(side="right", fill="y")

# Add horizontal scrollbar
#h_scrollbar = tk.Scrollbar(cv_scrollbar_frame, orient="horizontal", command=my_canvas.xview)
#h_scrollbar.pack(side="bottom", fill="x")

my_canvas.config(width=w, height=h)
my_canvas.pack(side="left", expand=True, fill="both")

# Configure the canvas to use the scrollbars
#my_canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)



# Background
bg = my_canvas.create_image(200, 0, anchor='center', image=background_image)

# bind mouse left-click on canvas
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
arrow_top_pil = Image.open(resources_dir / 'Gui' / 'arrow_top.png').resize((21, 21))
arrow_top = ImageTk.PhotoImage(arrow_top_pil)

arrow_up_pil = Image.open(resources_dir / 'Gui' / 'arrow_up.png').resize((21, 21))
arrow_up = ImageTk.PhotoImage(arrow_up_pil)

arrow_down_pil = Image.open(resources_dir / 'Gui' / 'arrow_down.png').resize((21, 21))
arrow_down = ImageTk.PhotoImage(arrow_down_pil)

arrow_bottom_pil = Image.open(resources_dir / 'Gui' / 'arrow_bottom.png').resize((21, 21))
arrow_bottom = ImageTk.PhotoImage(arrow_bottom_pil)

top_button= tk.Button(root, image=arrow_top, borderwidth=0, highlightthickness=0, command=topCallBack)
top_button.grid(column=3, row=1, sticky='w', padx=pad+5, pady=2)

up_button = tk.Button(root, image=arrow_up, borderwidth=0, highlightthickness=0, command=upCallBack)
up_button.grid(column=3, row=2, sticky='w', padx=pad+5, pady=2)

down_button = tk.Button(root, image=arrow_down, borderwidth=0, highlightthickness=0, command=downCallBack)
down_button.grid(column=3, row=3, sticky='w', padx=pad+5, pady=2)

bottom_button = tk.Button(root, image=arrow_bottom, borderwidth=0, highlightthickness=0, command=bottomCallBack)
bottom_button.grid(column=3, row=4, sticky='w', padx=pad+5, pady=2)

# Pool Tree
tree_frame = tk.Frame(root)
tree_scrollbar = tk.Scrollbar(tree_frame)
tree_scrollbar.pack(side='right', fill='y')
gear_tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
gear_tree.pack(fill='both', expand=True)

gear_tree.config(yscrollcommand=tree_scrollbar.set)
tree_scrollbar.config(command=gear_tree.yview)
tree_frame.grid(column=0, row=1, columnspan=2, rowspan=5, sticky='nswe', padx=pad)

# Add parent items with icons
drums_icon = tk.PhotoImage(file=resources_dir / 'Gui' / 'drums_icon.png')
cymbals_icon = tk.PhotoImage(file=resources_dir / 'Gui' / 'cymbals_icon.png')
other_icon = tk.PhotoImage(file=resources_dir / 'Gui' / 'other_icon.png')
drums_id = gear_tree.insert("", tk.END, text=" Drums", image=drums_icon)
cymbals_id = gear_tree.insert("", tk.END, text=" Cymbals", image=cymbals_icon)
other_id = gear_tree.insert("", tk.END, text=" Other", image=other_icon)

# Add Button
add_button = tk.Button(root, text ="add", command=addCallBack)
add_button.grid(column=0, row=6, sticky='nswe', padx=2*pad, pady=pad)

# Remove Button
remove_button = tk.Button(root, text="remove", command= removeCallBack)
remove_button.grid(column=1, row=6, sticky='nswe', padx=2*pad, pady=pad)

# Used Elements Listbox
listbox_frame = tk.Frame(root)
listbox_scrollbar = tk.Scrollbar(listbox_frame)
listbox_scrollbar.pack(side='right', fill='y')
listbox = tk.Listbox(listbox_frame, exportselection=False)
listbox.pack(fill='both', expand=True)

listbox.config(yscrollcommand=listbox_scrollbar.set)
listbox_scrollbar.config(command=listbox.yview)
listbox_frame.grid(column=0, row=7, columnspan=2, sticky='nswe', padx=pad+1)
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
bg_box.grid(column = 5, row = 0, sticky='e', padx=pad)

bg_box.bind('<<ComboboxSelected>>', bgCallBack)


# Gear Pop-up
def gear_popup():
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
    

# Exit Pop-up
def gearlist_popup():
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
    
    
# Exit Pop-up
def exit_popup():
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
    tk.Button(top, text="Yes", command=root.quit).grid(column=0, row=1, sticky='nswe', padx=10, pady=20)
    tk.Button(top, text="No", command=lambda: close_top(top)).grid(column=1, row=1, sticky='nswe', padx=10, pady=20)
    

# New Pop-up
def new_popup():
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
    global arr_step
    if arr_step > 3:
        arr_step -= 3
    
def arr_step_inc():
    global arr_step
    if arr_step < 20:
        arr_step += 3


# Select all button
def allCallBack():
    global all_selected, selected
    if all_selected:
        all_selected = False
        selected = 0
        for key in elements:
            elements[key].dehighlight([])
            elements[key].is_selected = False
    else:
        selected = 0
        for key in elements:
            elements[key].highlight([])
        all_selected = True

all_button = tk.Button(root, text="Select all", command= allCallBack)
all_button.grid(column=0, row=8, sticky='nswe', padx=pad, pady=pad)

# Rotation Slider
rot_slider = tk.Scale(root, from_=-179, to=179, orient='horizontal', command=sliderCallBack)
rot_slider.grid(column=4, row=8, columnspan=2, sticky='nswe', padx=50)

# Flip Checkbutton
flip_checkbutton = tk.Checkbutton(root, text='Flip cymbal', command=flip_change, state='disabled')
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
helpmenu.add_command(label="Decrease move step (arrows)", command=arr_step_dec)
helpmenu.add_command(label="Increase move step (arrows)", command=arr_step_inc)
#helpmenu.add_command(label="Background...") #drop down menu? under canvas or menu bar?
menubar.add_cascade(label="Edit", menu=helpmenu) # ask for save before...

root.config(menu=menubar)

    
# Append two rows to the CSV file for testing
#new_element = {"name": "Crash", "type": "cymbal", "is_circular": 1, "size": 22, "flippable": 1, "default_path": resources_dir / "Cymbals" / "22_crash.png", "flipped_path": resources_dir / "Cymbals" / "22_crash_f.png"}
#append_to_csv(gear_file, new_element)
#new_element = {"name": "Bell", "type": "cymbal", "is_circular": 1, "size": 8, "flippable": 1, "default_path": resources_dir / "Cymbals" / "8_bell.png", "flipped_path": resources_dir / "Cymbals" / "8_bell_f.png"}
#append_to_csv(gear_file, new_element)
# ["name", "type", "is_circular", "size", "flippable", "default_path", "flipped_path"]

def write_gear_file():
    kram = [["22\" Tama Bassdrum SP", "drum", 0, 25, 0, "Drums/22_tama_sp.png", "Drums/22_tama_sp.png"],###
            ["22\" Tama Bassdrum DP", "drum", 0, 25, 0, resources_dir / "Drums" / "22_tama_dp.png", resources_dir / "Drums" / "22_tama_dp.png"],###
            ["22\" Istanbul Ride", "cymbal", 1, 22, 1, resources_dir / "Cymbals" / "22_istanbul.png", resources_dir / "Cymbals" / "22_istanbul_f.png"],###
            ["22\" Paiste Flat Ride", "cymbal", 1, 22, 1, resources_dir / "Cymbals" / "22_paiste.png", resources_dir / "Cymbals" / "22_paiste_f.png"],###
            ["21\" Zildjian Ride", "cymbal", 1, 21, 1, resources_dir / "Cymbals" / "21_zildjian.png", resources_dir / "Cymbals" / "21_zildjian_f.png"],###
            ["20\" Zultan Ride", "cymbal", 1, 20, 1, resources_dir / "Cymbals" / "20_zultan.png", resources_dir / "Cymbals" / "20_zultan_f.png"],###
            ["20\" Masterwork Ride", "cymbal", 1, 20, 1, resources_dir / "Cymbals" / "20_masterwork.png", resources_dir / "Cymbals" / "20_masterwork_f.png"],###
            ["20\" Altes China", "cymbal", 1, 20, 1, resources_dir / "Cymbals" / "20_alt.png", resources_dir / "Cymbals" / "20_alt_f.png"],###
            ["19\" Sabian XSR Crash", "cymbal", 1, 19, 1, resources_dir / "Cymbals" / "19_sabian_xsr.png", resources_dir / "Cymbals" / "19_sabian_xsr_f.png"],###
            ["19\" Sabian Paragon China", "cymbal", 1, 19, 1, resources_dir / "Cymbals" / "19_sabian_paragon.png", resources_dir / "Cymbals" / "19_sabian_paragon_f.png"],###
            ["18\" Sabian HHX Crash", "cymbal", 1, 18, 1, resources_dir / "Cymbals" / "18_sabian_hhx.png", resources_dir / "Cymbals" / "18_sabian_hhx_f.png"],###
            ["18\" Sabian AAX Crash", "cymbal", 1, 18, 1, resources_dir / "Cymbals" / "18_sabian_aax.png", resources_dir / "Cymbals" / "18_sabian_aax_f.png"],###
            ["16\" Zultan Crash", "cymbal", 1, 16, 1, resources_dir / "Cymbals" / "16_zultan.png", resources_dir / "Cymbals" / "16_zultan_f.png"],###
            ["16\" Paiste PSTX Crash", "cymbal", 1, 16, 1, resources_dir / "Cymbals" / "16_paiste_pstx.png", resources_dir / "Cymbals" / "16_paiste_pstx_f.png"],###
            ["16\" Millenium China", "cymbal", 1, 16, 1, resources_dir / "Cymbals" / "16_millenium.png", resources_dir / "Cymbals" / "16_millenium_f.png"],###
            ["16\" Paiste Crash", "cymbal", 1, 16, 1, resources_dir / "Cymbals" / "16_paiste.png", resources_dir / "Cymbals" / "16_paiste_f.png"], ###16
            ["16\" Tama Floortom", "drum", 1, 16, 1, resources_dir / "Drums" / "16_tama.png", resources_dir / "Drums" / "16_tama.png"],###
            ["14\" Zultan HiHat", "cymbal", 1, 14, 0, resources_dir / "Cymbals" / "14_zultan.png", resources_dir / "Cymbals" / "14_zultan.png"],###
            ["14\" Paiste HiHat", "cymbal", 1, 14, 0, resources_dir / "Cymbals" / "14_paiste.png", resources_dir / "Cymbals" / "14_paiste.png"], ### paiste
            ["14\" Millenium Crash", "cymbal", 1, 14, 1, resources_dir / "Cymbals" / "14_millenium.png", resources_dir / "Cymbals" / "14_millenium_f.png"],###
            ["13\" Zultan HiHat", "cymbal", 1, 13, 0, resources_dir / "Cymbals" / "13_zultan.png", resources_dir / "Cymbals" / "13_zultan.png"],###
            ["13\" Tama Racktom", "drum", 1, 13, 0, resources_dir / "Drums" / "13_tama.png", resources_dir / "Drums" / "13_tama.png"],###
            ["13\" JJ Snare", "drum", 1, 13, 0, resources_dir / "Drums" / "13_pearl.png", resources_dir / "Drums" / "13_pearl.png"],###
            ["12\" Tama Racktom", "drum", 1, 12, 0, resources_dir / "Drums" / "12_tama.png", resources_dir / "Drums" / "12_tama.png"],###
            ["12\" Meinl Filter China", "cymbal", 1, 12, 1, resources_dir / "Cymbals" / "12_meinl.png", resources_dir / "Cymbals" / "12_meinl_f.png"],###
            ["12\" Wuhan China", "cymbal", 1, 12, 1, resources_dir / "Cymbals" / "12_wuhan.png", resources_dir / "Cymbals" / "12_wuhan_f.png"],###
            ["12\" Paiste Splash", "cymbal", 1, 12, 1, resources_dir / "Cymbals" / "12_paiste.png", resources_dir / "Cymbals" / "12_paiste_f.png"],###
            ["10\" Wuhan China", "cymbal", 1, 10, 1, resources_dir / "Cymbals" / "10_wuhan.png", resources_dir / "Cymbals" / "10_wuhan_f.png"],###
            ["10\" Paiste Splash", "cymbal", 1, 10, 1, resources_dir / "Cymbals" / "10_paiste.png", resources_dir / "Cymbals" / "10_paiste_f.png"],###
            ["10\" Gretsch Snare", "drum", 1, 10, 0, resources_dir / "Drums" / "10_gretsch.png", resources_dir / "Drums" / "10_gretsch.png"],###
            ["8\" Zultan Splash", "cymbal", 1, 8, 1, resources_dir / "Cymbals" / "8_zultan.png", resources_dir / "Cymbals" / "8_zultan_f.png"],###
            ["8\" Zultan Splash (Broken)", "cymbal", 1, 8, 1, resources_dir / "Cymbals" / "8_zultan_broken.png", resources_dir / "Cymbals" / "8_zultan_broken_f.png"],###
            ["8\" Paiste Bell", "cymbal", 1, 8, 1, resources_dir / "Cymbals" / "8_paiste.png", resources_dir / "Cymbals" / "8_paiste_f.png"],###
            ["8\" Meinl Ching Ring", "other", 1, 8, 1, resources_dir / "Other" / "8_meinl_ching.png", resources_dir / "Other" / "8_meinl_ching.png"],###
            ["6\" Stagg Splash (Thin)", "cymbal", 1, 6, 1, resources_dir / "Cymbals" / "6_stagg_thin.png", resources_dir / "Cymbals" / "6_stagg_thin_f.png"],###1st
            ["6\" Stagg Splash (Heavy)", "cymbal", 1, 6, 1, resources_dir / "Cymbals" / "6_stagg_heavy.png", resources_dir / "Cymbals" / "6_stagg_heavy_f.png"],###2nd
            ["6\" Stagg Bell", "cymbal", 1, 6, 1, resources_dir / "Cymbals" / "6_stagg_bell.png", resources_dir / "Cymbals" / "6_stagg_bell_f.png"],###
            ["6\" Octoban (High)", "drum", 1, 6, 0, resources_dir / "Drums" / "6_octoban_low.png", resources_dir / "Drums" / "6_octoban_low.png"],###1st
            ["6\" Octoban (Low)", "drum", 1, 6, 0, resources_dir / "Drums" / "6_octoban_low.png", resources_dir / "Drums" / "6_octoban_low.png"],###2nd
            ["Sonor Throne", "other", 1, 12, 0, resources_dir / "Other" / "throne.png", resources_dir / "Other" / "throne.png"],###
            ["Pearl HiHat Machine", "other", 0, 26, 0, resources_dir / "Other" / "pearl_tilted.png", resources_dir / "Other" / "pearl_tilted.png"],###
            ["Pearl Left Pedal", "other", 0, 13, 0, resources_dir / "Other" / "pearl_lp.png", resources_dir / "Other" / "pearl_lp.png"],
            ["Pearl Cowbell", "other", 0, 9, 0, resources_dir / "Other" / "pearl_cowbell.png", resources_dir / "Other" / "pearl_cowbell.png"]]###
    
    if True: #not gear_file.is_file():   # Writes the gear.csv file newly every time the code is executed (for accurate image paths), might optimize in the future
        # File does not exists
        with open(gear_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=column_names_gear)
            writer.writeheader()
    
    for k in kram:
        new_element = {"name": k[0], "type": k[1], "is_circular": k[2], "size": k[3], "flippable": k[4], "default_path": k[5], "flipped_path": k[6]}
        with open(gear_file, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=column_names_gear)
            writer.writerow(new_element)
    

# Uncomment to (re-)write the gear.csv file
write_gear_file()

# Delete a row from the CSV file
#delete_from_csv("elements.csv", 0)  # Delete the first row
    

# Create Instrument instances
row_count = 0
with open(gear_file, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        instruments.append(Instrument(row_count))
        row_count += 1
        
update_tree()
for instr in instruments:
    print(instr.name)

# "Are you sure?" pop up for closing
root.protocol('WM_DELETE_WINDOW', exit_popup)

root.mainloop()