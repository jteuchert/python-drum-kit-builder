# View: handling the GUI components and layout

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

# Modules
import config

class AppView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.root = master
        self.root.geometry(str(config.WINDOW_SIZE[0]) + 'x' + str(config.WINDOW_SIZE[1]))
        self.root.resizable(width=False, height=False)
        self.set_title(config.DEFAULT_TITLE)


        # Background images (needs structural change)
        self.background_image = Image.open(config.RESOURCES_DIR / "Environment" / "floor.jpg")
        self.background_image = ImageTk.PhotoImage(self.background_image)

        self.none_image = Image.open(config.RESOURCES_DIR / "Environment" / "none.png")
        self.none_image = ImageTk.PhotoImage(self.none_image)


        # Window icon, does generally not work with .ico on Ubuntu
        if not config.ON_LINUX:
            self.root.iconbitmap(config.RESOURCES_DIR / "Gui" / "8_zultan.ico")


        # Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=40)
        self.grid_columnconfigure(4, weight=40)
        self.grid_columnconfigure(5, weight=40)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=30)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=50)
        self.grid_rowconfigure(8, weight=1)
        self.grid_rowconfigure(9, weight=1)
        
        # Existing widgets
        self.pool_label = tk.Label(self, text= "Instruments pool").grid(column=0, row=0, sticky='nswe')

        self.cv_scrollbar_frame = tk.Frame(self)
        self.cv_scrollbar_frame.grid(column=3, row=1, rowspan=7, columnspan=3, sticky='nswe', padx=config.WIDGET_PAD)

        # Canvas
        self.my_canvas = tk.Canvas(self.cv_scrollbar_frame, 
                                   highlightbackground="gray", 
                                   highlightthickness=2, 
                                   width=config.CANVAS_WIDTH, 
                                   height=config.CANVAS_HEIGHT, 
                                   scrollregion=config.CANVAS_SCROLLREGION, 
                                   bg="white"
                                   )
        print("Canvas created with size:", config.CANVAS_WIDTH, config.CANVAS_HEIGHT)
        self.my_canvas.config(width=config.CANVAS_WIDTH, height=config.CANVAS_HEIGHT)
        self.my_canvas.pack(side="left", expand=True, fill="both")

        # Layer Buttons
        arrow_top_pil = Image.open(config.RESOURCES_DIR / 'Gui' / 'arrow_top.png').resize((21, 21))
        self.arrow_top = ImageTk.PhotoImage(arrow_top_pil)

        arrow_up_pil = Image.open(config.RESOURCES_DIR / 'Gui' / 'arrow_up.png').resize((21, 21))
        self.arrow_up = ImageTk.PhotoImage(arrow_up_pil)

        arrow_down_pil = Image.open(config.RESOURCES_DIR / 'Gui' / 'arrow_down.png').resize((21, 21))
        self.arrow_down = ImageTk.PhotoImage(arrow_down_pil)

        arrow_bottom_pil = Image.open(config.RESOURCES_DIR / 'Gui' / 'arrow_bottom.png').resize((21, 21))
        self.arrow_bottom = ImageTk.PhotoImage(arrow_bottom_pil)

        self.top_button= tk.Button(self, image=self.arrow_top, borderwidth=0, highlightthickness=0)
        self.top_button.grid(column=3, row=1, sticky='w', padx=config.WIDGET_PAD+5, pady=2)

        self.up_button = tk.Button(self, image=self.arrow_up, borderwidth=0, highlightthickness=0)
        self.up_button.grid(column=3, row=2, sticky='w', padx=config.WIDGET_PAD+5, pady=2)

        self.down_button = tk.Button(self, image=self.arrow_down, borderwidth=0, highlightthickness=0)
        self.down_button.grid(column=3, row=3, sticky='w', padx=config.WIDGET_PAD+5, pady=2)

        self.bottom_button = tk.Button(self, image=self.arrow_bottom, borderwidth=0, highlightthickness=0)
        self.bottom_button.grid(column=3, row=4, sticky='w', padx=config.WIDGET_PAD+5, pady=2)

        # Gear pool tree
        self.tree_frame = tk.Frame(self)
        self.tree_scrollbar = tk.Scrollbar(self.tree_frame)
        self.tree_scrollbar.pack(side='right', fill='y')
        self.gear_tree = ttk.Treeview(self.tree_frame, show="tree", selectmode="browse")
        self.gear_tree.pack(fill='both', expand=True)

        self.gear_tree.config(yscrollcommand=self.tree_scrollbar.set)
        self.tree_scrollbar.config(command=self.gear_tree.yview)
        self.tree_frame.grid(column=0, row=1, columnspan=2, rowspan=5, sticky='nswe', padx=config.WIDGET_PAD)

        # Add parent items with icons
        self.drums_icon = tk.PhotoImage(file=config.DRUMS_ICON_PATH)
        self.cymbals_icon = tk.PhotoImage(file=config.CYMBALS_ICON_PATH)
        self.other_icon = tk.PhotoImage(file=config.OTHER_ICON_PATH)
        self.drums_id = self.gear_tree.insert("", tk.END, text=" Drums", image=self.drums_icon)
        self.cymbals_id = self.gear_tree.insert("", tk.END, text=" Cymbals", image=self.cymbals_icon)
        self.other_id = self.gear_tree.insert("", tk.END, text=" Other", image=self.other_icon)

        # Add Button
        self.add_button = tk.Button(self, text ="add")
        self.add_button.grid(column=0, row=6, sticky='nswe', padx=2*config.WIDGET_PAD, pady=config.WIDGET_PAD)

        # Remove Button
        self.remove_button = tk.Button(self, text="remove")
        self.remove_button.grid(column=1, row=6, sticky='nswe', padx=2*config.WIDGET_PAD, pady=config.WIDGET_PAD)

        # Used Elements Listbox
        self.listbox_frame = tk.Frame(self)
        self.listbox_scrollbar = tk.Scrollbar(self.listbox_frame)
        self.listbox_scrollbar.pack(side='right', fill='y')
        self.listbox = tk.Listbox(self.listbox_frame, exportselection=False)
        self.listbox.pack(fill='both', expand=True)

        self.listbox.config(yscrollcommand=self.listbox_scrollbar.set)
        self.listbox_scrollbar.config(command=self.listbox.yview)
        self.listbox_frame.grid(column=0, row=7, columnspan=2, sticky='nswe', padx=config.WIDGET_PAD+1)


        n = tk.StringVar() 
        self.bg_box = ttk.Combobox(self, width = 27, textvariable=n, state='readonly') 
        self.bg_box['values'] = ('wood floor 1', 'none')
        self.bg_box.current(0)
        self.bg_box.grid(column = 5, row = 0, sticky='e', padx=config.WIDGET_PAD)


        self.select_all_button = tk.Button(self, text="Select all")
        self.select_all_button.grid(column=0, row=8, sticky='nswe', padx=config.WIDGET_PAD, pady=config.WIDGET_PAD)

        # Rotation Slider
        self.rot_slider = tk.Scale(self, from_=-179, to=179, orient='horizontal')
        self.rot_slider.grid(column=4, row=8, columnspan=2, sticky='nswe', padx=50)

        # Flip Checkbutton
        self.flip_checkbutton = tk.Checkbutton(self, text='Flip cymbal', state='disabled')
        self.flip_checkbutton.grid(column=3, row=8)

        # Menu bar
        self.menubar = tk.Menu(self)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)

        self.root.config(menu=self.menubar)

        self.background_instance = self.my_canvas.create_image(200, 0, anchor='center', image=self.background_image)


    def get_real_canvas_size(self):
        canv_width = self.my_canvas.winfo_width()
        canv_height = self.my_canvas.winfo_height()
        return canv_width, canv_height

    # Set up binds
    def set_closing_protocol(self, handler=None):
        """ Bind window closing to handler """
        self.root.protocol('WM_DELETE_WINDOW', handler)

    def bind_background_selection(self, handler=None):
        """ Bind background selection combobox to handler """
        self.bg_box.bind('<<ComboboxSelected>>', handler)

    def bind_add_button(self, handler=None):
        """ Bind add button to handler """
        self.add_button.config(command=handler)

    def bind_remove_button(self, handler=None):
        """ Bind remove button to handler """
        self.remove_button.config(command=handler)

    def bind_select_all_button(self, handler=None):
        """ Bind select all button to handler """
        self.select_all_button.config(command=handler)

    def bind_top_button(self, handler=None):
        """ Bind top layer button to handler """
        self.top_button.config(command=handler)

    def bind_up_button(self, handler=None):
        """ Bind layer up button to handler """
        self.up_button.config(command=handler)

    def bind_down_button(self, handler=None):
        """ Bind layer down button to handler """
        self.down_button.config(command=handler)

    def bind_bottom_button(self, handler=None):
        """ Bind bottom layer button to handler """
        self.bottom_button.config(command=handler)

    def bind_canvas_click(self, handler=None):
        """ Bind mouse click on canvas to handler """
        self.my_canvas.bind("<Button-1>", handler)

    def bind_arrow_keys(self, handler=None):
        """ Bind arrow keys to handler """
        for key in ["<Left>", "<Right>", "<Up>", "<Down>"]:
            self.root.bind(key, handler)

    def bind_listbox_selection(self, handler=None):
        """ Bind listbox selection to handler """
        self.listbox.bind("<<ListboxSelect>>", handler)

    def bind_rotation_slider(self, handler=None):
        """ Bind rotation slider to handler """
        self.rot_slider.config(command=handler)

    def bind_flip_checkbutton(self, handler=None):
        """ Bind flip checkbutton to handler """
        self.flip_checkbutton.config(command=handler)

    def build_menu(self, commands: dict):
        """" Build Menu Bar """
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Edit", menu=self.helpmenu)

        self.filemenu.add_command(label="New", command=commands["new"])
        self.filemenu.add_command(label="Load...", command=commands["load"])
        self.filemenu.add_command(label="Save", command=commands["save"])
        self.filemenu.add_command(label="Save as...", command=commands["save_as"])
        self.filemenu.add_command(label="Save image as...", command=commands["save_image"])
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=commands["exit"])

        self.helpmenu.add_command(label="View gear", command=commands["view_gear"])
        self.helpmenu.add_command(label="Increase move step (arrows)", command=commands["increase_move_step"])
        self.helpmenu.add_command(label="Decrease move step (arrows)", command=commands["decrease_move_step"])

    def raise_all_markers(self, elements):
        """ Move up all markers in order to ensure correct selectability """
        for layer in elements:
            self.my_canvas.tag_raise(elements[layer].el_view.marker)

    def update_listbox(self, elements, selected):
        """ Update contents of used gear listbox """
        # Clear listbox
        self.listbox.delete('0','end')
        # Repopulate listbox
        for layer in elements:
            self.listbox.insert(0, elements[layer].el_model.instr.name)
        self.listbox.selection_clear('0','end')
        # Select selected item in listbox
        if selected != 0:
            last = len(elements)
            self.listbox.select_set(last - selected)

    def get_listbox_selection(self):
        """ Get selected item from used gear listbox """
        listbox_selection = self.listbox.curselection()
        if listbox_selection:
            index = listbox_selection[0]
            # Convert listbox index to layer
            layer = len(self.listbox.get(0, 'end')) - index
            return layer
        return 0

    def refresh_gear_tree(self, instruments):
        """ Update gear tree """
        # Delete each child item
        child_items = self.gear_tree.get_children(self.drums_id)
        for child in child_items:
            self.gear_tree.delete(child)
        child_items = self.gear_tree.get_children(self.cymbals_id)
        for child in child_items:
            self.gear_tree.delete(child)
        child_items = self.gear_tree.get_children(self.other_id)
        for child in child_items:
            self.gear_tree.delete(child)

        # Repopulate tree
        for inst in instruments:
            if inst.type == "drum" and not inst.is_used:
                self.gear_tree.insert(self.drums_id, tk.END, text=inst.name)
            if inst.type == "cymbal" and not inst.is_used:
                self.gear_tree.insert(self.cymbals_id, tk.END, text=inst.name)
            if inst.type == "other" and not inst.is_used:
                self.gear_tree.insert(self.other_id, tk.END, text=inst.name)

    def update_rot_slider(self, angle):
        """ Update rotation slider value """
        self.rot_slider.set(-angle)

    def activate_flip_checkbutton(self, el_model):
        """ Enable flip checkbutton """
        if el_model.instr.flippable:
            self.flip_checkbutton.configure(state='normal')
            if el_model.flipped:
                self.flip_checkbutton.select()
            else:
                self.flip_checkbutton.deselect()
        else:
            # Deactivate if element not flippable
            self.deactivate_flip_checkbutton()
        
    def deactivate_flip_checkbutton(self):
        """ Disable flip checkbutton """
        self.flip_checkbutton.configure(state='disabled')
        self.flip_checkbutton.deselect()

    def swap_up(self, layer, elements):
        """ Swap lower with upper element on canvas """
        self.my_canvas.tag_raise(elements[layer].el_view.image, elements[layer + 1].el_view.edge)
        self.my_canvas.tag_raise(elements[layer].el_view.edge, elements[layer].el_view.image)
        self.raise_all_markers(elements)

    def show_gear_popup(self, instruments):
        """ Gear popup """
        # Make pop-up window
        top = tk.Toplevel(self)
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


    def show_new_dialog(self, on_confirm):
        """ New project popup """
        # Make popup window
        top = tk.Toplevel(self)
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

        def confirm():
            on_confirm()
            top.destroy()

        def cancel():
            top.destroy()

        tk.Label(top, text= "Are you sure you want to reset?").grid(column=0, row=0, columnspan=2, sticky='nswe', pady=10)
        tk.Button(top, text="Yes", command=confirm).grid(column=0, row=1, sticky='nswe', padx=10, pady=20)
        tk.Button(top, text="No", command=cancel).grid(column=1, row=1, sticky='nswe', padx=10, pady=20)


    def show_quit_dialog(self, on_confirm):
        """ Exit confirmation popup """
        top = tk.Toplevel(self.root)
        top.geometry("210x130+300+300")
        top.title("Exit")

        top.attributes("-topmost", 1)
        top.grab_set()

        # Grid
        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=1)
        top.grid_rowconfigure(0, weight=1)
        top.grid_rowconfigure(1, weight=1)
        top.grid_rowconfigure(2, weight=2)

        tk.Label(top, text="Are you sure you want to exit?").grid(column=0, row=0, columnspan=2, pady=4)
        tk.Label(top, text="Unsaved changes will be discarded.").grid(column=0, row=1, columnspan=2, pady=2)

        def confirm():
            top.destroy()
            on_confirm()

        def cancel():
            top.destroy()

        tk.Button(top, text="Yes", command=confirm).grid(column=0, row=2, padx=10, pady=10, sticky="nswe")
        tk.Button(top, text="No", command=cancel).grid(column=1, row=2, padx=10, pady=10, sticky="nswe")

    def show_save_image_dialog(self):
        """ Open file dialog for saving image file """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", 
            filetypes=[("PNG files", "*.png")], 
            initialdir=config.KITS_DIR
            )
    
        if file_path:
            return file_path
        

    def show_save_project_dialog(self):
        """ Open file dialog for saving project file """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("CSV files", "*.csv")], 
            initialdir=config.KITS_DIR
            )
    
        if file_path:
            return file_path

    def show_load_project_dialog(self):
        """ Open file dialog for loading project file """
        file_path = filedialog.askopenfilename(
            defaultextension=".csv", 
            filetypes=[("CSV files", "*.csv")],
            initialdir=config.KITS_DIR
            )
    
        if file_path:
            return file_path
        
    def show_image_saved_message(self):
        """ Create message box to verify saved image """
        messagebox.showinfo("Saved", "Image saved successfully.")

    def show_project_saved_message(self):
        """ Create message box to verify saved project """
        messagebox.showinfo("Saved", "Kit saved successfully.")

    def set_title(self, title):
        """ Change aindow title """
        self.root.title(title)

    def set_background(self):
        """ Set background image """
        value = self.bg_box.get()
        if value == 'wood floor 1':
            self.my_canvas.itemconfig(self.background_instance, image=self.background_image)
        if value == 'none':
            self.my_canvas.itemconfig(self.background_instance, image=self.none_image)