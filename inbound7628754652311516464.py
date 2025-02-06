# gui.py

import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import cv2
from image_processor import ImageProcessor
from utils import cv2_to_tkinter

class ImageEditorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Editor")
        self.root.state("zoomed")

        self.processor = ImageProcessor()

        # Create a frame at the top for buttons
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Load Image Button
        self.load_button = tk.Button(self.top_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Save Image Button
        self.save_button = tk.Button(self.top_frame, text="Save Image", command=self.save_image)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Frame for original image
        self.original_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.original_frame.pack(side=tk.LEFT, padx=4, pady=2)

        self.original_label = tk.Label(self.original_frame, text="Original Image", font=("Arial", 16))
        self.original_label.pack(pady=2)

        self.original_canvas = tk.Canvas(self.original_frame, width=800, height=500, bg="white")
        self.original_canvas.pack()

        # Frame for cropped image
        self.cropped_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.cropped_frame.pack(side=tk.RIGHT, padx=2, pady=2)

        self.cropped_label = tk.Label(self.cropped_frame, text="Cropped Image", font=("Arial", 16))
        self.cropped_label.pack(pady=2)

        self.cropped_canvas = tk.Canvas(self.cropped_frame, width=450, height=500, bg="white")
        self.cropped_canvas.pack()

        # Bind keyboard shortcuts
        self.root.bind("<Control-o>", lambda event: self.load_image())
        self.root.bind("<Control-s>", lambda event: self.save_image())

        # Variables for cropping
        self.start_x = self.start_y = self.end_x = self.end_y = self.rect_id = None

        # Bind mouse events for selection
        self.original_canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.original_canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.original_canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        # Slider for resizing the cropped image
        self.resize_slider = tk.Scale(self.top_frame, from_=10, to=200, orient=tk.HORIZONTAL, label="Resize (%)", command=self.resize_cropped_image)
        self.resize_slider.set(100)  # Set default to 100%
        self.resize_slider.pack(side=tk.LEFT, padx=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
        if file_path:
            self.processor.load_image(file_path)
            self.display_thumbnail()

    def display_thumbnail(self):
        """ Display the original image as a thumbnail. """
        if self.processor.image is not None:
            self.tk_image = cv2_to_tkinter(self.processor.image, max_size=(800, 500))

            # Clear canvas before redrawing
            self.original_canvas.delete("all")

            # Draw image at the computed position
            self.original_canvas.create_image(400, 250, image=self.tk_image, anchor=tk.CENTER)
            self.original_canvas.image = self.tk_image  # Prevent garbage collection

    def on_mouse_press(self, event):
        """ Store initial mouse click position adjusted for image offset. """
        if self.processor.image is not None:
            self.start_x = event.x
            self.start_y = event.y

            # Remove previous selection rectangle
            if self.rect_id:
                self.original_canvas.delete(self.rect_id)

    def on_mouse_drag(self, event):
        """ Update the selection rectangle while dragging and display the cropped image. """
        if self.start_x is not None and self.start_y is not None:
            # Remove previous rectangle and draw the new selection
            if self.rect_id:
                self.original_canvas.delete(self.rect_id)
            self.rect_id = self.original_canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y, outline="red"
            )

            # Update the cropped image
            self.end_x = event.x
            self.end_y = event.y
            self.processor.inverse_crop(self.start_x, self.start_y, self.end_x, self.end_y)
            self.display_cropped_image()

    def on_mouse_release(self, event):
        """ Apply inverse cropping when the mouse button is released. """
        if self.processor.image is not None and self.start_x is not None and self.start_y is not None:
            self.end_x = event.x
            self.end_y = event.y
            
            # Perform inverse cropping and display the cropped image
            self.processor.inverse_crop(self.start_x, self.start_y, self.end_x, self.end_y)
            self.display_cropped_image()

    def display_cropped_image(self):
        """ Display the cropped image based on the selected area. """
        if (self.processor.image is not None and 
            self.start_x is not None and 
            self.start_y is not None and 
            self.end_x is not None and 
            self.end_y is not None):
            
            x1 = min(self.start_x, self.end_x)
            y1 = min(self.start_y, self.end_y)
            x2 = max(self.start_x, self.end_x)
            y2 = max(self.start_y, self.end_y)

            # Check for valid cropping area
            if x1 < 0 or y1 < 0 or x2 > self.processor.image.shape[1] or y2 > self.processor.image.shape[0]:
                print("Error: Selection is out of bounds!")
                return

            # Crop the original image to the selected area
            cropped_image = self.processor.image[y1:y2, x1:x2]

            # Check if cropped image is empty
            if cropped_image.size == 0:
                print("Error: Cropped image is empty!")
                return

            self.processor.cropped_image = cropped_image  # Store the cropped image for saving

            # Convert to Tkinter format for displaying
            self.tk_cropped_image = cv2_to_tkinter(cropped_image, max_size=(450, 500))

            # Calculate width and height of the cropped image
            cropped_width = x2 - x1
            cropped_height = y2 - y1

            # Center the image based on its dimensions
            center_x = 225 - (cropped_width // 2)  # Assuming 450 is the canvas width
            center_y = 250 - (cropped_height // 2)  # Assuming 500 is the canvas height

            # Clear the cropped canvas before displaying the new image
            self.cropped_canvas.delete("all")

            # Display the cropped image at the calculated center position
            self.cropped_canvas.create_image(center_x, center_y, image=self.tk_cropped_image, anchor=tk.CENTER)
            self.cropped_canvas.image = self.tk_cropped_image

    def resize_cropped_image(self, value):
        """ Resize the cropped image based on the slider value. """
        if self.processor.cropped_image is not None:
            # Get the current percentage from the slider
            percent = int(value)

            # Calculate new dimensions based on the percentage
            new_width = int(self.processor.cropped_image.shape[1] * (percent / 100))
            new_height = int(self.processor.cropped_image.shape[0] * (percent / 100))

            # Resize the cropped image for preview
            resized_image = cv2.resize(self.processor.cropped_image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

            # Convert to Tkinter format for displaying
            self.tk_resized_image = cv2_to_tkinter(resized_image, max_size=(450, 500))

            # Clear the cropped canvas before displaying the resized image
            self.cropped_canvas.delete("all")

            # Center the resized image based on its dimensions
            center_x = 225 - (new_width // 2)
            center_y = 250 - (new_height // 2)

            # Display the resized image at the calculated center position
            self.cropped_canvas.create_image(center_x, center_y, image=self.tk_resized_image, anchor=tk.CENTER)
            self.cropped_canvas.image = self.tk_resized_image  # Prevent garbage collection

    def save_image(self):
        """ Save the modified image to the local device in the 'output' directory. """
        if self.processor.cropped_image is not None:
            # Set the initial directory to the 'output' folder
            initial_dir = "output"
            
            # Create the 'output' directory if it doesn't exist
            if not os.path.exists(initial_dir):
                os.makedirs(initial_dir)

            # Define a default filename (you can customize this)
            default_filename = "cropped_image.png"  # or any other default name you prefer

            # Ask the user for a filename to save
            file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                    initialdir=initial_dir,
                                                    initialfile=default_filename,
                                                    filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg")])
            if file_path:
                try:
                    success = cv2.imwrite(file_path, self.processor.cropped_image)
                    if success:
                        messagebox.showinfo("Success", "Image saved successfully!")
                    else:
                        messagebox.showerror("Error", "Failed to save the image.")
                        print("Error: Failed to save the image. Please check the file path and permissions.")
                except Exception as e:
                    messagebox.showerror("Error", "An error occurred while saving the image.")
                    print(f"Error: {e}")  # Print the exception to the terminal
        else:
            messagebox.showwarning("Warning", "No cropped image to save.")



    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageEditorGUI()
    app.run()
