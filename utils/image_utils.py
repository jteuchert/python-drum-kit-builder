from PIL import Image, ImageTk

def instrument_image(path, angle):
    """ Create element image, rotated correctly """
    pil_img_resize = Image.open(path)
    pil_image_resize_rotated = pil_img_resize.rotate(angle, resample=Image.BICUBIC, expand=True)
    img = ImageTk.PhotoImage(pil_image_resize_rotated)
    return img