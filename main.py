import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog, ttk
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import webbrowser
import cv2
from mtcnn import MTCNN
from PIL import Image

# Ensure necessary directories exist
os.makedirs("logs", exist_ok=True)

# Initialize MTCNN face detector
detector = MTCNN()

# Function to log error messages to a log file
def log_error(message):
    with open(os.path.join("logs", "error_log.txt"), "a") as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")

# Logging function for compliance
def log_user_acceptance():
    """Log the user's acceptance of the terms."""
    with open(os.path.join("logs", "acceptance_log.txt"), "a") as log_file:
        log_file.write(f"User accepted terms on {datetime.now()}\n")

# Function to show GDPR and legal compliance modal
def show_compliance_modal():
    """Display a compliance modal to ensure user understands legal ramifications."""
    modal = tk.Toplevel()
    modal.title("Legal Disclaimer")
    modal.geometry("400x300")
    modal.transient(root)  # Keep it on top
    modal.grab_set()  # Focus on this modal
    modal.resizable(False, False)

    # Set the favicon for the modal
    modal.iconphoto(False, tk.PhotoImage(file="data/favicon.png"))

    # Centering the modal
    modal.update_idletasks()
    width = modal.winfo_width()
    height = modal.winfo_height()
    x = (modal.winfo_screenwidth() // 2) - (width // 2)
    y = (modal.winfo_screenheight() // 2) - (height // 2)
    modal.geometry(f'{width}x{height}+{x}+{y}')

    label = tk.Label(modal, text="Important Legal Notice", font=("Arial", 14, "bold"))
    label.pack(pady=10)

    text = (
        "Web scraping photographs of individuals without their consent may be illegal "
        "under GDPR and other privacy regulations. You are responsible for ensuring that "
        "your actions comply with all applicable laws. By proceeding, you acknowledge "
        "that you understand the legal ramifications."
    )
    
    text_box = scrolledtext.ScrolledText(modal, wrap=tk.WORD, width=40, height=8, font=("Arial", 10))
    text_box.insert(tk.END, text)
    text_box.configure(state="disabled")
    text_box.pack(pady=10)

    agreement_var = tk.IntVar()

    agreement_check = tk.Checkbutton(modal, text="I understand and agree to the terms", variable=agreement_var)
    agreement_check.pack(pady=5)

    def on_accept():
        """Handle user acceptance of the disclaimer."""
        if agreement_var.get() == 1:
            log_user_acceptance()
            modal.destroy()  # Close the modal
            root.deiconify()  # Show the main window after agreement
        else:
            messagebox.showwarning("Warning", "You must agree to the terms to proceed.")

    accept_button = tk.Button(modal, text="Accept", command=on_accept)
    accept_button.pack(pady=10)

    # Prevent closing the modal with the window close button
    modal.protocol("WM_DELETE_WINDOW", lambda: None)
    
    # Use wait_window with a try-except to catch any issues
    try:
        root.wait_window(modal)  # Wait for the modal to be closed
    except tk.TclError:
        pass  # Handle the case where the window was closed

# Scrape images from a search engine (example: Google Images)
def scrape_images(name, pages=2):
    """Scrape image URLs from Google Images based on the search query and number of pages."""
    images = []
    for page in range(pages):
        search_query = name.replace(" ", "+")
        url = f"https://www.google.com/search?hl=en&tbm=isch&q={search_query}&start={page * 20}"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/58.0.3029.110 Safari/537.3"
            )
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.text, "html.parser")

            for img in soup.find_all("img"):
                img_url = img.get("src")
                if img_url and "http" in img_url and img_url not in images:
                    images.append(img_url)  # Collect unique image URLs

            print(f"Page {page + 1}: Found {len(images)} images so far.")

        except requests.RequestException as e:
            log_error(f"Error while scraping images: {e}")
            messagebox.showerror("Error", "Failed to scrape images. Please try again.")
            return []

    return images

# Function to download images and log URLs
def download_images(images, name):
    """Download images from URLs and log the URLs to a file."""
    img_dir = os.path.join("downloads", name)
    os.makedirs(img_dir, exist_ok=True)

    download_count = 0
    urls_list = []

    for idx, img_url in enumerate(images):
        if stop_downloads:  # Stop downloading if user requests
            break
        try:
            img_data = requests.get(img_url).content
            img_path = os.path.join(img_dir, f"{name}_image_{idx + 1}.jpg")
            with open(img_path, "wb") as img_file:
                img_file.write(img_data)

            download_count += 1
            urls_list.append(img_url)  # Store the URL of the downloaded image

            # Update progress bar and counter
            progress_bar['value'] = (download_count / len(images)) * 100  # Update progress bar as a percentage
            download_counter_label.config(text=f"Downloaded: {download_count}/{len(images)}")
            root.update_idletasks()

        except Exception as e:
            log_error(f"Error while downloading image {img_url}: {e}")
            print(f"Failed to download image {img_url}: {e}")

    # Save the URLs and other information to a file in the image directory
    log_downloads(urls_list, download_count, img_dir)

# Function to log downloaded URLs and counts
def log_downloads(urls_list, download_count, img_dir):
    """Log the downloaded image URLs to a file."""
    with open(os.path.join(img_dir, "downloads_url.txt"), "w") as url_file:
        url_file.write(f"Downloaded {download_count} images:\n\n")
        for url in urls_list:
            url_file.write(f"{url}\n")
    print(f"Logged {download_count} image URLs to {os.path.join(img_dir, 'downloads_url.txt')}.")

# Function to open the downloaded folder
def open_downloaded_folder(name):
    """Open the folder containing the downloaded images."""
    img_dir = os.path.join("downloads", name)
    webbrowser.open(f'file://{os.path.abspath(img_dir)}')

# Function to stop downloads
def stop_downloading():
    """Stop the ongoing image download process."""
    global stop_downloads
    stop_downloads = True
    open_folder_button.config(state=tk.NORMAL)  # Enable the open folder button

# Function to detect faces in an image and return details like bounding boxes
def detect_faces(image_path):
    """Detect faces in an image and return details like bounding boxes."""
    img = cv2.imread(image_path)
    
    # Check if the image was successfully loaded
    if img is None:
        print(f"Error: Unable to load image at {image_path}")
        log_error(f"Error: Unable to load image at {image_path}")
        return []  # Return an empty list indicating no faces detected

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = detector.detect_faces(img_rgb)
    
    return faces

# Function to score detected faces based on size, centeredness, and clarity
def score_face(face, image_width, image_height):
    """Score the detected face based on size, centeredness, and clarity."""
    x, y, width, height = face['box']
    face_center_x = x + width / 2
    face_center_y = y + height / 2

    # Face size relative to image size
    size_score = (width * height) / (image_width * image_height)

    # Centeredness score: How close the face center is to the image center
    center_score = 1 - ((abs(face_center_x - image_width / 2) / (image_width / 2)) + (abs(face_center_y - image_height / 2) / (image_height / 2))) / 2

    # Combined score
    return size_score * center_score

# Function to process images in a directory and select the best ones based on face detection
def process_images(image_dir, selected_dir):
    """Process images in the directory, selecting the best ones based on face detection."""
    os.makedirs(selected_dir, exist_ok=True)
    
    # List of valid image extensions
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

    for img_name in os.listdir(image_dir):
        # Check if the file has a valid image extension
        if not img_name.lower().endswith(valid_extensions):
            print(f"Skipping non-image file: {img_name}")
            continue
        
        img_path = os.path.join(image_dir, img_name)
        faces = detect_faces(img_path)

        if not faces:
            print(f"No faces detected in {img_name}")
            continue

        # Assuming the best face is the one with the highest score
        img = Image.open(img_path)
        img_width, img_height = img.size

        best_face = max(faces, key=lambda face: score_face(face, img_width, img_height))
        best_score = score_face(best_face, img_width, img_height)

        # If the score is above a threshold, save the image
        if best_score > 0.5:  # Adjust this threshold as necessary
            img.save(os.path.join(selected_dir, img_name))
            print(f"Selected {img_name} with a score of {best_score}")

# Update search_images function to include face detection
def search_images():
    """Handle the image search process initiated by the user."""
    global stop_downloads, current_name
    stop_downloads = False
    current_name = simpledialog.askstring("Search Query", "Enter the name of the person:", parent=root)
    if not current_name:
        return
    
    # Ask user for the number of pages to scrape
    pages = simpledialog.askinteger("Number of Pages", "Enter the number of pages to scrape:", parent=root, minvalue=1, maxvalue=10)
    if pages is None:
        return  # User canceled the input

    # Enable the Stop Downloading button after search is initiated
    stop_button.config(state=tk.NORMAL)

    # Reset progress bar and counter label
    progress_bar['value'] = 0
    download_counter_label.config(text="Downloaded: 0/0")

    # Proceed with scraping after acceptance
    images = scrape_images(current_name, pages)
    download_images(images, current_name)

    # Process downloaded images for face detection
    img_dir = os.path.join("downloads", current_name)
    selected_dir = os.path.join("downloads", current_name, "selected")

    # Show a modal indicating face detection is starting
    messagebox.showinfo("Processing Images", "Starting face detection and selection process.")
    process_images(img_dir, selected_dir)
    messagebox.showinfo("Processing Complete", f"Face detection and selection complete. Selected images saved to {selected_dir}")

# Function to create and show the main application window
def create_main_window():
    """Set up the main application window and its components."""
    root.title("VisageSearch")
    root.geometry("400x300")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')  # Center the main window

    # Set the favicon for the main window
    root.iconphoto(False, tk.PhotoImage(file="data/favicon.png"))

    # Title Label
    title_label = tk.Label(root, text="VisageSearch", font=("Arial", 20, "bold"))
    title_label.pack(pady=10)

    # Instructions
    instructions_label = tk.Label(root, text="Enter the name of the person to search for their photos.")
    instructions_label.pack(pady=5)

    # Search Button
    search_button = tk.Button(root, text="Search", command=search_images, font=("Arial", 12), bg="lightblue", relief="flat")
    search_button.pack(pady=10)

    # Stop Button with Icon
    global stop_button
    stop_button = tk.Button(root, text="🛑", command=stop_downloading, font=("Arial", 20), bg="lightcoral", width=3, relief="flat", state=tk.DISABLED)
    stop_button.pack(pady=5)

    # Open Folder Button (initially disabled)
    global open_folder_button
    open_folder_button = tk.Button(root, text="Open Downloaded Folder", command=lambda: open_downloaded_folder(current_name), font=("Arial", 12), state=tk.DISABLED)
    open_folder_button.pack(pady=5)

    # Download Counter Label
    global download_counter_label
    download_counter_label = tk.Label(root, text="Downloaded: 0/0")
    download_counter_label.pack(pady=5)

    # Visual Progress Bar
    global progress_bar
    progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
    progress_bar.pack(pady=10)

# Initialize root window but keep it hidden initially
root = tk.Tk()
root.withdraw()

# Create the main window layout (but keep it hidden)
create_main_window()

# Show the compliance modal first
show_compliance_modal()

# Start the application event loop
root.mainloop()
