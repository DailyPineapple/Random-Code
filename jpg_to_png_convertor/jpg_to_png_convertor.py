import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import io
import threading
import concurrent.futures
from flask import Blueprint, request, send_from_directory, jsonify, render_template

jpg_to_png_bp = Blueprint('html_to_pdf', __name__, template_folder='templates')
class App:
    def __init__(self, root):
        self.root = root
        self.failed_conversions = []
        self.skipped_files = []
        self.folder_selected = ''
        self.total_files = 0
        self.converted_files = 0
        self.cancel_conversion = False
        self.executor = None  # Executor for ThreadPool

        self.root.title("JPEG to PNG Converter")
        self.root.geometry("600x400")  # Adjusted for new layout

        self.label = tk.Label(root, text="Select a directory to convert JPEGs to PNGs", pady=10)
        self.label.pack()

        self.selected_folder_label = tk.Label(root, text="No directory selected", pady=5, fg="blue")
        self.selected_folder_label.pack()

        self.choose_button = tk.Button(root, text="Choose Directory", command=self.choose_directory)
        self.choose_button.pack(pady=5)

        self.start_button = tk.Button(root, text="Start Conversion", command=self.start_conversion_thread, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        self.cancel_button = tk.Button(root, text="Cancel Conversion", command=self.cancel_conversion_thread, state=tk.DISABLED)
        self.cancel_button.pack(pady=5)

        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=20)

        self.status_label = tk.Label(root, text="", pady=10)
        self.status_label.pack()

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def choose_directory(self):
        self.folder_selected = filedialog.askdirectory()
        if self.folder_selected:
            self.selected_folder_label.config(text=f"Selected Directory: {self.folder_selected}")
            self.update_status("Scanning for JPEG files...")
            self.total_files = self.count_jpeg_files(self.folder_selected)
            if self.total_files > 0:
                self.update_status(f"Ready to convert {self.total_files} files. Click 'Start Conversion' to begin.")
                self.start_button.config(state=tk.NORMAL)
            else:
                self.update_status("No JPEG files found in the selected directory.")

    def count_jpeg_files(self, root_dir):
        count = 0
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg')):
                    count += 1
        return count

    def start_conversion_thread(self):
        self.cancel_conversion = False
        self.cancel_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        num_workers = os.cpu_count() - 2
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_workers)  # Adjust number of workers as needed
        conversion_thread = threading.Thread(target=self.convert_jpeg_to_png, args=(self.folder_selected,))
        conversion_thread.start()

    def cancel_conversion_thread(self):
        if self.executor:
            self.executor.shutdown(wait=False)  # This will halt the executor immediately, canceling all pending futures
            self.executor = None
        self.cancel_conversion = True
        self.update_status("Conversion cancelled.")
        self.cancel_button.config(state=tk.DISABLED)


    def convert_jpeg_to_png(self, root_dir):
        files_to_convert = [os.path.join(root, file)
                            for root, dirs, files in os.walk(root_dir)
                            for file in files if file.lower().endswith(('.jpg', '.jpeg'))]

        self.progress['maximum'] = len(files_to_convert)
        futures = [self.executor.submit(self.convert_image_to_png, path) for path in files_to_convert]

        for future in concurrent.futures.as_completed(futures):
            if self.cancel_conversion:
                break  # Early exit if cancellation requested
            self.converted_files += 1
            self.update_progress()
            result = future.result()
            if "Failed" in result:
                self.failed_conversions.append(result)

        self.root.after(0, self.conversion_complete)

    def convert_image_to_png(self, image_path):
        try:
            with Image.open(image_path) as img:
                in_mem_file = io.BytesIO()
                img.save(in_mem_file, format="PNG")
                png_size = in_mem_file.tell()
                original_size = os.path.getsize(image_path)

            if png_size >= original_size:
                png_path = image_path.rsplit('.', 1)[0] + '.png'
                with open(png_path, 'wb') as f:
                    f.write(in_mem_file.getvalue())
                os.remove(image_path)
                return f"Converted: {image_path}"
            else:
                self.skipped_files.append(image_path)
                return f"Skipped (PNG larger): {image_path}"
        except Exception as e:
            return f"Failed to convert {image_path}: {e}"

    def update_progress(self):
        self.root.after(0, lambda: self.progress.configure(value=self.converted_files))
        self.update_status(f"Converting images in ({self.converted_files}/{self.total_files})")

    def conversion_complete(self):
        if not self.cancel_conversion:
            report = "Conversion complete."
            if self.failed_conversions:
                report += f" Failed: {len(self.failed_conversions)}."
            if self.skipped_files:
                report += f" Skipped: {len(self.skipped_files)}."
            messagebox.showinfo("Conversion Finished", report)
            self.update_status("Conversion finished. You may choose another directory.")
        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.converted_files = 0  # Reset converted files count for next run
        self.progress['value'] = 0  # Reset progress bar

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
