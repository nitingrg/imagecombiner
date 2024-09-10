import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

# Initialize global variables
image_paths = []
zoom_level = 1.0  # Used for manual zoom in and out
combined_image = None  # To keep the combined image for zooming and preview updates
preview_photo = None  # To keep a reference to the photo used in the label

def update_combined_image():
    global combined_image
    if not image_paths:
        combined_image = None
        return

    images = [Image.open(path) for path in image_paths]
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)

    combined_image = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for img in images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width

def calculate_initial_zoom():
    if not combined_image:
        return 1.0  # Default zoom level if no image is loaded

    # Determine the maximum preview size
    max_preview_width = 800  # Adjust as needed
    max_preview_height = 600  # Adjust as needed

    width_ratio = max_preview_width / combined_image.width
    height_ratio = max_preview_height / combined_image.height
    return min(width_ratio, height_ratio)

def update_preview(use_initial_zoom=False):
    global combined_image, preview_photo
    update_combined_image()  # Ensure the combined image is up-to-date

    if combined_image is None:
        preview_label.config(image='')
        return

    zoom_factor = calculate_initial_zoom() if use_initial_zoom else zoom_level

    try:
        zoomed_width = int(combined_image.width * zoom_factor)
        zoomed_height = int(combined_image.height * zoom_factor)
        display_image = combined_image.resize((zoomed_width, zoomed_height), Image.Resampling.LANCZOS)

        preview_photo = ImageTk.PhotoImage(display_image)
        preview_label.config(image=preview_photo)
        preview_label.image = preview_photo  # Keep a reference
    except Exception as e:
        status_label.config(text=f"Error updating preview: {e}")

def zoom_in():
    global zoom_level
    zoom_level *= 1.1  # Increase zoom level by 10%
    update_preview()

def zoom_out():
    global zoom_level
    zoom_level *= 0.9  # Decrease zoom level by 10%
    update_preview()

def browse_image():
    filenames = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.png;*.gif;*.bmp")])
    for filename in filenames:
        image_paths.append(filename)
        image_listbox.insert(tk.END, filename)
    update_preview(use_initial_zoom=True)

def remove_image():
    selected_indices = list(image_listbox.curselection())
    for index in reversed(selected_indices):
        del image_paths[index]
        image_listbox.delete(index)
    update_preview(use_initial_zoom=True)

def remove_all_images():
    image_paths.clear()
    image_listbox.delete(0, tk.END)
    update_preview(use_initial_zoom=True)

def browse_output_path():
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
    if file_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, file_path)

def combine_images():
    if combined_image and len(image_paths) >= 2:
        output_path = output_entry.get()
        if not output_path.endswith(('.jpg', '.png')):
            status_label.config(text="Please specify a valid output path with .jpg or .png extension.")
            return
        combined_image.save(output_path)
        status_label.config(text="Images combined successfully.")
    else:
        status_label.config(text="Please add and select at least 2 images to combine.")

def move_selection(offset):
    selected_indices = list(image_listbox.curselection())
    if not selected_indices:
        return

    for i in selected_indices:
        if 0 <= i + offset < len(image_paths):
            # Move in Listbox
            image_listbox.delete(i)
            image_listbox.insert(i + offset, image_paths[i + offset])

            # Move in image_paths
            image_paths.insert(i + offset, image_paths.pop(i))
            image_listbox.selection_set(i + offset)

    update_preview(use_initial_zoom=True)

def move_up():
    move_selection(-1)

def move_down():
    move_selection(1)

# UI Setup
root = tk.Tk()
root.title("Image Combiner")
root.geometry("800x600")

style = ttk.Style(root)
style.theme_use("clam")

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

control_frame = ttk.Frame(main_frame, padding="10")
control_frame.pack(fill=tk.X)

listbox_frame = ttk.Frame(main_frame, padding="10")
listbox_frame.pack(fill=tk.BOTH, expand=True)

output_frame = ttk.Frame(main_frame, padding="10")
output_frame.pack(fill=tk.X)

preview_frame = ttk.Frame(main_frame, padding="10")
preview_frame.pack(fill=tk.BOTH, expand=True)

status_frame = ttk.Frame(main_frame, padding="10")
status_frame.pack(fill=tk.X)

browse_button = ttk.Button(control_frame, text="Browse", command=browse_image)
browse_button.pack(side=tk.LEFT, padx=5)

remove_button = ttk.Button(control_frame, text="Remove", command=remove_image)
remove_button.pack(side=tk.LEFT, padx=5)

remove_all_button = ttk.Button(control_frame, text="Remove All", command=remove_all_images)
remove_all_button.pack(side=tk.LEFT, padx=5)

zoom_in_button = ttk.Button(control_frame, text="Zoom In", command=zoom_in)
zoom_in_button.pack(side=tk.LEFT, padx=5)

zoom_out_button = ttk.Button(control_frame, text="Zoom Out", command=zoom_out)
zoom_out_button.pack(side=tk.LEFT, padx=5)

move_up_button = ttk.Button(control_frame, text="Move Up", command=move_up)
move_up_button.pack(side=tk.LEFT, padx=5)

move_down_button = ttk.Button(control_frame, text="Move Down", command=move_down)
move_down_button.pack(side=tk.LEFT, padx=5)

image_listbox = tk.Listbox(listbox_frame, width=50, height=10, selectmode=tk.EXTENDED)
image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

listbox_scroll = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=image_listbox.yview)
listbox_scroll.pack(side=tk.RIGHT, fill=tk.Y)
image_listbox.config(yscrollcommand=listbox_scroll.set)

output_label = ttk.Label(output_frame, text="Output Path:")
output_label.pack(side=tk.LEFT, padx=5)

output_entry = ttk.Entry(output_frame, width=50)
output_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

output_browse_button = ttk.Button(output_frame, text="Browse", command=browse_output_path)
output_browse_button.pack(side=tk.LEFT, padx=5)

combine_button = ttk.Button(output_frame, text="Combine", command=combine_images)
combine_button.pack(side=tk.RIGHT, padx=5)

preview_label = ttk.Label(preview_frame)
preview_label.pack(fill=tk.BOTH, expand=True)

status_label = ttk.Label(status_frame, text="", background='light grey')
status_label.pack(fill=tk.X)

root.mainloop()