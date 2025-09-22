# capture.py
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import shutil
import os
from PIL import Image
import face_recognition

DATASET_DIR = "dataset"

def save_face_image(image_path, name):
    person_dir = os.path.join(DATASET_DIR, name)
    os.makedirs(person_dir, exist_ok=True)
    image_count = len(os.listdir(person_dir)) + 1
    dest_path = os.path.join(person_dir, f"{name}_{image_count}.jpg")
    shutil.copy(image_path, dest_path)
    messagebox.showinfo("Success", f"Saved as {dest_path}")

def upload_photo():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if not file_path:
        return

    # Check if image contains a valid face
    img = face_recognition.load_image_file(file_path)
    faces = face_recognition.face_locations(img)
    if len(faces) == 0:
        messagebox.showerror("Error", "No face detected in image!")
        return

    name = simpledialog.askstring("Input", "Enter Name:")
    if name:
        save_face_image(file_path, name)
    else:
        messagebox.showerror("Error", "Name cannot be empty!")

if __name__ == "__main__":
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)

    root = tk.Tk()
    root.title("Upload Face Photo")
    root.geometry("300x150")

    btn = tk.Button(root, text="Upload Photo", command=upload_photo, height=3, width=20)
    btn.pack(pady=40)

    root.mainloop()
