import math

def rotate_point(x, y, angle):
    """ Rotate point, for rotated rectangle """
    # Convert angle from degrees to radians
    rad = math.radians(-angle) # negative for correct rotation direction
    
    # Calculate new coordinates
    new_x = x * math.cos(rad) - y * math.sin(rad)
    new_y = x * math.sin(rad) + y * math.cos(rad)  
    return new_x, new_y