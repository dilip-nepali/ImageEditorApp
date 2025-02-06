# utils.py

from PIL import Image, ImageTk
import cv2

def cv2_to_tkinter(cv_image, max_size=(800, 500)):
    """ Convert OpenCV image to Tkinter-compatible format while maintaining aspect ratio. """
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(cv_image)

    # Calculate the new size while maintaining aspect ratio
    image_pil.thumbnail(max_size, Image.Resampling.LANCZOS)

    return ImageTk.PhotoImage(image_pil)
