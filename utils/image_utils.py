from PIL import Image, ImageTk
import config

def instrument_image(path, angle):
    """ Create element image, rotated correctly """
    pil_img_resize = Image.open(path)
    pil_image_resize_rotated = pil_img_resize.rotate(angle, resample=Image.BICUBIC, expand=True)
    img = ImageTk.PhotoImage(pil_image_resize_rotated)
    return img

def render_project_image(real_canvas_size, elements):
    """ Render and return image of current project """
    # Create a new blank image using Pillow
    image = Image.new("RGBA", real_canvas_size, (255, 255, 255, 0))  # Transparent background

    # Background, needs fix (position, scale, different bgs)
    bg_img = Image.open(config.RESOURCES_DIR / "Environment" / "floor.jpg")
    image.paste(bg_img, (0, 0))
    
    # Iterate over the image items
    for layer in elements:
        # Get the image's position and the PIL image object
        coords = elements[layer].el_model.pos
        if elements[layer].el_model.flipped:
            image_path = elements[layer].el_model.instr.flipped_path
        else:
            image_path = elements[layer].el_model.instr.default_path
        
        pillow_image = Image.open(image_path)
        pillow_image_rot = pillow_image.rotate(elements[layer].el_model.rot, resample=Image.BICUBIC, expand=True)            
        
        # Adjust anchors: on canvas, anchor is center. for the pillow image it is the top-left corner
        image_width, image_height = pillow_image_rot.size
        x, y = int(coords[0]) - image_width // 2, int(coords[1]) - image_height // 2

        # Paste the image onto the blank image
        image.paste(pillow_image_rot, (x, y), pillow_image_rot)
    return image
