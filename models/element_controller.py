# Element Controller: handling element events (connecting view and model)

from utils import geometry

class ElementController:
    def __init__(self, el_model, el_view, app_controller):
        self.el_model = el_model
        self.el_view = el_view
        self.app = app_controller

        # Create edge and marker in view
        self.el_view.set_edge_and_marker(
            self.el_model.instr.is_circular, 
            self.el_model.instr.r, self.el_model.pos
        )

        # Binds
        self.el_view.bind_marker(
            enter=self.on_enter, 
            leave=self.on_leave, 
            drag_start=self.on_drag_start, 
            drag_stop=self.on_drag_stop, 
            drag=self.on_drag
        )

        # Select self
        self.el_model.is_selected = True
        self.app.model.selected = self.el_model.layer
        self.el_view.highlight([])

    
    # Mouse click
    def mouse_click(self):
        # Move this logic into controller.py?
        """ Changing elements' state of being selected (T/F) when mouse is clicked on canvas """
        if self.app.model.hovering == self.el_model.layer:
            self.el_model.is_selected = True
            self.app.model.selected = self.el_model.layer
            self.app.view.rot_slider.set(-self.el_model.rot)
            self.el_view.highlight(None)
        else:
            self.el_model.is_selected = False
            self.el_view.dehighlight(None)

    def move_element(self, dx, dy, selection_edges=None):
        """ Move element by (dx, dy), checking canvas bounds """
        if self.el_model.is_selected:
            x_border, y_border = self.el_view.get_canvas_borders()
            # Get current position or selection edges
            selection_edges = (
                selection_edges if selection_edges 
                else (self.el_model.pos[0], 
                      self.el_model.pos[0], 
                      self.el_model.pos[1], 
                      self.el_model.pos[1])
            )

            # Check if movement would go out of canvas bound
            if (selection_edges[1] + dx <= x_border 
                and selection_edges[0] + dx >= 0 
                and selection_edges[3] + dy <= y_border 
                and selection_edges[2] + dy >= 0
            ):
                self.el_model.move(dx, dy)
                self.el_view.move(dx, dy)

    def on_enter(self, event):
        """ Mouse entering element marker """
        self.el_view.highlight(event)
        self.app.model.hovering = self.el_model.layer

    def on_leave(self, event):
        """ Mouse leaving element marker """
        self.app.model.hovering = 0
        if (not self.app.model.all_selected 
            and not self.el_model.is_selected
        ):
            self.el_view.dehighlight(event)

    def on_drag_start(self, event):
        """ Beginning drag of an element """
        # record the item and its location
        self.el_model.drag_data_x = event.x
        self.el_model.drag_data_y = event.y

    def on_drag_stop(self, event):
        """ End drag of an element """
        # reset the drag information
        self.el_model.drag_data_x = 0
        self.el_model.drag_data_y = 0

    def on_drag(self, event):
        """ Handle dragging of an element """
        # compute how much the mouse has moved
        delta_x = event.x - self.el_model.drag_data_x
        delta_y = event.y - self.el_model.drag_data_y

        # move the object
        self.move_element(delta_x, delta_y)

        # record the new position
        self.el_model.drag_data_x = event.x
        self.el_model.drag_data_y = event.y

    def rotate(self, angle):
        """ Rotate element to angle """
        # Update model and update texture
        self.el_model.rot = angle
        self.el_view.update_texture()
        
        # Rotate edge and marker shape if rectangular
        if not self.el_model.instr.is_circular:
            position = self.el_model.pos
            new_points = []
            for i in range(0, 8, 2):
                x, y = self.el_model.polygon_points[i], self.el_model.polygon_points[i+1]
                rotated = geometry.rotate_point(x, y, angle)
                new_points.append(rotated[0] + position[0])
                new_points.append(rotated[1] + position[1])
            self.el_view.canvas.coords(self.el_view.edge, new_points)
            self.el_view.canvas.coords(self.el_view.marker, new_points)

        """
        # Update view
        self.el_view.canvas.delete(self.el_view.image)
        self.el_view.texture = self.el_view._load_texture()
        self.el_view.image = self.el_view.canvas.create_image(
            *self.el_model.pos, anchor="center", image=self.el_view.texture
        )
        """
    def flip(self):
        """ Flip element if possible """
        if self.el_model.instr.flippable:
            self.el_model.flipped = not self.el_model.flipped
            self.el_view.update_texture()
