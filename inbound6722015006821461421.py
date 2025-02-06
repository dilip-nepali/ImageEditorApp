# image_processor.py

import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        self.image = None
        self.original_image = None  # Keep a copy of the original
        self.cropped_image = None   # Store the processed image

    def load_image(self, file_path):
        """ Load an image from the file system. """
        self.image = cv2.imread(file_path)
        self.original_image = self.image.copy()

    def inverse_crop(self, x1, y1, x2, y2):
        """ Crop the selected area and invert it (remove selection). """
        if self.image is None:
            return

        # Ensure coordinates are in the correct order
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])

        # Create a mask to remove the selected region
        mask = np.ones(self.image.shape[:2], dtype=np.uint8) * 255  # White mask
        mask[y1:y2, x1:x2] = 0  # Black where the selection is

        # Apply the mask to the original image
        self.cropped_image = cv2.bitwise_and(self.image, self.image, mask=mask)
