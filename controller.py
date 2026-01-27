# Controller: handling user input and application logic (connecting view and model)

import config
from models.element_model import ElementModel
from models.element_view import ElementView
from models.element_controller import ElementController
from utils import image_utils
from utils import csv_io
import csv
import ast

class AppController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Menu commands
        self.view.build_menu({
            "new": self.on_new,
            "load": self.on_load,
            "save": self.on_save,
            "save_as": self.on_save_as,
            "save_image": self.on_save_image,
            "exit": self.on_quit_requested,
            "view_gear": self.on_view_gear,
            "increase_move_step": self.on_increase_move_step,
            "decrease_move_step": self.on_decrease_move_step
            })

        # Binds
        self.view.bind_canvas_click(handler=self.on_canvas_click)
        self.view.bind_arrow_keys(handler=self.on_arrow_pressed)
        self.view.bind_select_all_button(handler=self.on_select_all)
        self.view.bind_add_button(handler=self.on_add)
        self.view.bind_remove_button(handler=self.on_remove)
        self.view.bind_listbox_selection(handler=self.on_listbox_selection)
        self.view.bind_rotation_slider(handler=self.on_rotation_changed)
        self.view.bind_flip_checkbutton(handler=self.on_flip_state_changed)
        self.view.bind_top_button(handler=self.on_top_layer)
        self.view.bind_up_button(handler=self.on_up_layer)
        self.view.bind_down_button(handler=self.on_down_layer)
        self.view.bind_bottom_button(handler=self.on_bottom_layer)
        self.view.bind_background_selection(handler=self.on_background_selection)

        # "Are you sure?" popup for closing
        self.view.set_closing_protocol(handler=self.on_quit_requested)

        self.initialize_app()


    def initialize_app(self):
        """ Initialize application state """
        self.model.load_instruments_from_csv(config.GEAR_FILE)
        self.view.refresh_gear_tree(self.model.instruments)


    def on_canvas_click(self, event):
        """ Mouse click handler for canvas"""
        print("canvas click at", event.x, event.y)
        self.model.all_selected = False
        # Deactivate flip checkbutton
        self.view.deactivate_flip_checkbutton()
        for layer in self.model.elements:
            self.model.elements[layer].mouse_click() # Possibly make this more efficient without calling mouse_click for all elements?

        # Update selected
        self.model.selected = 0
        for layer in self.model.elements:
            if self.model.elements[layer].el_model.is_selected:
                self.model.selected = layer
                self.view.activate_flip_checkbutton(
                    el_model=self.model.elements[self.model.selected].el_model
                )
                self.view.update_listbox(self.model.elements, self.model.selected) # this and next line needed?
                return
            
        # Update listbox
        self.view.update_listbox(self.model.elements, self.model.selected)

    def on_arrow_pressed(self, event):
        """ Handle arrow key presses to move selected elements """
        print("arrow pressed:", event.keysym)
        if self.model.all_selected:
            # Get selection edges for canvas boundary checking
            min_x = min(self.model.elements[layer].el_model.pos[0] for layer in self.model.elements)
            max_x = max(self.model.elements[layer].el_model.pos[0] for layer in self.model.elements)
            min_y = min(self.model.elements[layer].el_model.pos[1] for layer in self.model.elements)
            max_y = max(self.model.elements[layer].el_model.pos[1] for layer in self.model.elements)
            selection_edges = (min_x, max_x, min_y, max_y)
            selected_elements = self.model.elements.keys()
        else:
            selected_elements = [self.model.selected] if self.model.selected != 0 else []
            selection_edges = None
        for layer in selected_elements:
            if event.keysym == "Left":
                self.model.elements[layer].move_element(-self.model.arr_step, 0, selection_edges)
            elif event.keysym == "Right":
                self.model.elements[layer].move_element(self.model.arr_step, 0, selection_edges)
            elif event.keysym == "Up":
                self.model.elements[layer].move_element(0, -self.model.arr_step, selection_edges)
            elif event.keysym == "Down":
                self.model.elements[layer].move_element(0, self.model.arr_step, selection_edges)



    def on_select_all(self):
        """ Handle select all button press """
        print("select all pressed")
        self.model.selected = 0
        if self.model.all_selected:
            self.model.all_selected = False
            for layer in self.model.elements:
                self.model.elements[layer].el_model.is_selected = False
                self.model.elements[layer].el_view.dehighlight(None)
            return
        self.model.all_selected = True
        for layer in self.model.elements:
            self.model.elements[layer].el_model.is_selected = True
            self.model.elements[layer].el_view.highlight(None)
        self.view.deactivate_flip_checkbutton()
        if len(self.model.elements) == 1:
            # If only one element, set selected to it
            layer = 1
            self.model.selected = layer
            self.model.elements[layer].el_model.is_selected = True
            self.model.elements[layer].el_view.highlight(None)
            self.view.update_rot_slider(self.model.elements[layer].el_model.rot)
            self.view.activate_flip_checkbutton(
                el_model=self.model.elements[self.model.selected].el_model
            )

    def on_listbox_selection(self, event):
        """ Handle listbox selection """
        listbox_selection = self.view.get_listbox_selection()
        print("listbox selection:", listbox_selection)
        if listbox_selection != 0:
            # Deselect all
            self.model.all_selected = False
            for layer in self.model.elements:
                self.model.elements[layer].el_model.is_selected = False
                self.model.elements[layer].el_view.dehighlight(None)
            # Select the chosen one
            self.model.selected = listbox_selection
            self.model.elements[listbox_selection].el_model.is_selected = True
            self.model.elements[listbox_selection].el_view.highlight(None)
            self.view.update_rot_slider(self.model.elements[listbox_selection].el_model.rot)
            self.view.activate_flip_checkbutton(
                el_model=self.model.elements[self.model.selected].el_model
            )
        else:
            self.model.selected = 0

    def on_rotation_changed(self, event):
        """ Handle rotation slider change """
        if self.model.selected != 0:
            value = event
            print("rotation changed:", value)
            self.model.elements[self.model.selected].rotate(-int(value))

    def on_flip_state_changed(self):
        """ Handle flip checkbutton change """
        self.model.elements[self.model.selected].flip()



    def on_top_layer(self):
        """ Handle top layer button press """
        selected_layer = self.model.selected
        highest_layer = len(self.model.elements)
        for _ in range(selected_layer, highest_layer):
            self.on_up_layer()

    def on_up_layer(self):
        """ Handle layer up button press """
        selected_layer = self.model.selected
        # Swap selected element with element above, if not the highest element is selected
        if selected_layer < len(self.model.elements) and selected_layer > 0:
            self.layer_swap_control(layer=selected_layer, direction=1)

    def on_down_layer(self):
        """ Handle layer down button press """
        selected_layer = self.model.selected
        # Swap selected element with element below, if not the lowest element is selected
        if selected_layer > 1:
            self.layer_swap_control(layer=selected_layer, direction=-1)

    def on_bottom_layer(self):
        """ Handle bottom layer button press """
        selected_layer = self.model.selected
        for _ in range(1, selected_layer):
            self.on_down_layer()

    def layer_swap_control(self, layer=None, direction=None): 
        """ Handle swapping of two elements. Swapping direction: 1 --> up, -1 --> down """
        # Swap canvas elements
        self.view.swap_up(layer - (direction == -1), self.model.elements)

        # Adjust selected to new layer 
        self.model.selected = layer + direction

        # Update instance layers
        self.model.elements[layer].el_model.layer = layer + direction
        self.model.elements[layer + direction].el_model.layer = layer
            
        # Swap dictionary order
        tmp = self.model.elements[layer]
        self.model.elements[layer] = self.model.elements[layer + direction]
        self.model.elements[layer + direction] = tmp

        # Update markers
        self.view.raise_all_markers(self.model.elements)

        # Update listbox
        self.view.update_listbox(self.model.elements, self.model.selected)



    def on_quit_requested(self):
        """ Handle quit request """
        self.view.show_quit_dialog(on_confirm=self.on_quit_confirmed)

    def on_quit_confirmed(self):
        """ Quit application """
        self.view.root.destroy()

    def on_new(self):
        """ Handle new project request """
        print("new")
        self.view.show_new_dialog(on_confirm=self.reset_app)


    def reset_app(self):
        """ New project (reset app) """
        for _, instance in self.model.elements.items():
            instance.el_view.clear()
            del instance
    
        # Reset model variables (selected, elements...)
        self.model.reset_state()

        # Reset tree and listbox
        for inst in self.model.instruments:
            # Set all instruments to not used
            inst.is_used = False
        # Reset widgets
        self.view.refresh_gear_tree(self.model.instruments)
        self.view.update_listbox({}, 0)
        self.view.update_rot_slider(0)
        self.view.deactivate_flip_checkbutton()

        # Reset window title
        self.view.set_title(config.DEFAULT_TITLE)


    def on_load(self):
        """ Handle load project request """
        print("load")
        # Open file dialog for loading file
        file_path = self.view.show_load_project_dialog()
        if file_path:
            self.reset_app()
            with open(file_path, mode='r') as file:
                reader = csv.DictReader(file)
                new_layer = 1
                for row in reader:
                    self.create_element(int(row["ID"]), 
                                        int(row["layer"]), 
                                        pos=ast.literal_eval(row["position"]), 
                                        rot=int(row["rotation"]), 
                                        flipped=bool(int(row["flipped"]))
                                        )
                    self.model.elements[new_layer].rotate(int(row["rotation"])) # for now, can be more efficient
                    self.model.instruments[int(row["ID"])].is_used = True
                    new_layer += 1
        
            # Make sure all markers are on top
            self.view.raise_all_markers(self.model.elements)
        
            # Deselect all elements
            for layer in self.model.elements:
                self.view.my_canvas.itemconfig(self.model.elements[layer].el_view.edge, outline='')
                self.model.elements[layer].el_model.is_selected = False
            self.model.selected = 0
            self.view.update_listbox(self.model.elements, 0)
            self.view.refresh_gear_tree(self.model.instruments)

            self.model.save_path = file_path
            self.view.set_title(file_path)

    def on_save(self): # Can be structured more efficiently and more MVC style
        """ Handle save project request """
        print("save")
        save_path = self.model.save_path
        if save_path is not None:
            # clear file
            with open(save_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(config.COLUMN_NAMES)
        
            # Save to file
            for layer in self.model.elements:
                new_element = {"ID": self.model.elements[layer].el_model.instr.ID, 
                                "layer": self.model.elements[layer].el_model.layer, 
                                "position": self.model.elements[layer].el_model.pos, 
                                "rotation": self.model.elements[layer].el_model.rot, 
                                "flipped": int(self.model.elements[layer].el_model.flipped)
                                }
                csv_io.append_to_csv(save_path, new_element, config.COLUMN_NAMES)
            print("Data saved to:", save_path)
            self.view.show_project_saved_message()
        else:
            self.on_save_as()

    def on_save_as(self):
        """ Handle save as project request """
        print("save as")
        # Get save path from dialog
        file_path = self.view.show_save_project_dialog()

        if file_path:
            csv_io.save_to_csv(file_path, config.COLUMN_NAMES)
            self.model.save_path = file_path
            self.on_save()
            self.view.set_title(file_path)

    def on_save_image(self):
        """ Handle save image request """
        print("save image")
        # Get save path from dialog
        file_path = self.view.show_save_image_dialog()
        if file_path:
            # Save image
            # Ensure the layout is updated
            self.view.root.update_idletasks() # Not MVC

            # Get real canvas size
            canvas_size = self.view.get_real_canvas_size()

            # Render image
            image = image_utils.render_project_image(canvas_size, self.model.elements)
            
            # Save the final image
            image.save(file_path)
            self.view.show_image_saved_message()


    def on_view_gear(self):
        """ Handle view gear request """
        self.view.show_gear_popup(self.model.instruments)

    def on_increase_move_step(self):
        """ Handle increase move step request """
        if self.model.arr_step + config.ARR_STEP_INCREMENT <= 20:
            self.model.arr_step += config.ARR_STEP_INCREMENT
        print("increase move step:", self.model.arr_step)

    def on_decrease_move_step(self):
        """ Handle decrease move step request """
        if self.model.arr_step - config.ARR_STEP_INCREMENT >= 1:
            self.model.arr_step -= config.ARR_STEP_INCREMENT
        print("decrease move step:", self.model.arr_step)

    def on_add(self):
        """ Handle add element request """
        # Get selected item from gear tree
        selected_instrument = self.view.gear_tree.selection()
        selection_name = self.view.gear_tree.item(selected_instrument)['text']
        if selection_name == "":
            print("No instrument selected, cannot add element.")
            return
        
        print(f"Add element requested ({selection_name})")
        for id, instance in enumerate(self.model.instruments):
            if instance.name == selection_name:
                new_layer = len(self.model.elements) + 1
                self.create_element(id, new_layer)
        
                # Add name to listbox
                self.view.update_listbox(self.model.elements, new_layer)

                # Make sure all markers are on top
                self.view.raise_all_markers(self.model.elements)

                # Mark instrument as used
                instance.is_used = True

                # Update gear tree
                self.view.refresh_gear_tree(self.model.instruments)

                # Reset rotation slider
                self.view.update_rot_slider(0)

                # Activate flip button if applicable
                self.view.activate_flip_checkbutton(
                    el_model=self.model.elements[self.model.selected].el_model
                )
                break


    def on_remove(self):
        """ Handle remove element request """
        # Add option to remove all here?
        # Get selected element
        selected = self.model.selected
        if selected != 0:
            instr_index = self.model.elements[selected].el_model.instr.ID
            self.model.instruments[instr_index].is_used = False

            # Save current num of elements
            old_length = len(self.model.elements)
            # Remove selected element
            self.model.elements[selected].el_view.clear()
            del self.model.elements[selected]

            # Reorder layering
            # Iterate through elements, stopping before reaching the old dict length (new_length = old_length - 1)
            for i in range(selected, old_length):
                self.model.elements[i] = self.model.elements.pop(i+1)
                self.model.elements[i].layer = i

            # Set no selection
            self.model.selected = 0

            # Update listbox and gear tree
            self.view.update_listbox(self.model.elements, 0)
            self.view.refresh_gear_tree(self.model.instruments)

            self.view.deactivate_flip_checkbutton()

    def create_element(self, instr_id, new_layer, pos=config.SPAWN_POINT.copy(), rot=0, flipped=False):
        """ Create a new canvas element on given layer with given instrument ID """
        # Deselect other elements
        self.model.all_selected = False
        for layer in self.model.elements:
            self.model.elements[layer].el_model.is_selected = False
            self.model.elements[layer].el_view.dehighlight(None)

        # Get instrument to add
        new_instr = self.model.instruments[instr_id]

        # Create MVC for new element
        element_model = ElementModel(
            instr=new_instr,
            layer=new_layer,
            pos=pos,
            rot=rot,
            flipped=flipped
        )

        element_view = ElementView(
            canvas=self.view.my_canvas,
            el_model=element_model
        )

        element_controller = ElementController(
            el_model=element_model,
            el_view=element_view,
            app_controller=self
        )

        # Add to elements dictionary
        self.model.elements[new_layer] = element_controller


    def on_background_selection(self, event):
        """ Handle background image selection """
        self.view.set_background()
