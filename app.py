import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
from datetime import datetime

class VideoHandler(FileSystemEventHandler):
    def __init__(self, delay, callback):
        self.delay = delay
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.mp4', '.avi', '.mkv')):
            video_name = os.path.basename(event.src_path)
            detection_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.callback(f"{detection_time} - {video_name}")
            print(f"New video detected: {event.src_path}")
            time.sleep(self.delay)  # Add delay before playing
            self.play_video(event.src_path)

    def play_video(self, video_path):
        try:
            os.startfile(video_path)  # This works on Windows
        except AttributeError:
            # For non-Windows systems
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.call(('open', video_path))
            else:  # Linux and other Unix-like
                subprocess.call(('xdg-open', video_path))

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grey_wolf_auto_play")
        self.geometry("600x400")

        # Change this line to set your desired hot folder path
        self.hot_folder = r"D:\Custom Project\auto_play_video\hot_video"
        self.delay = 5  # Default delay in seconds

        self.create_widgets()
        self.start_watching()

    def create_widgets(self):
        self.create_settings_frame()
        self.create_video_list_frame()

    def create_settings_frame(self):
        settings_frame = ttk.LabelFrame(self, text="Settings")
        settings_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(settings_frame, text="Hot Folder:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.folder_label = ttk.Label(settings_frame, text=self.hot_folder)
        self.folder_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(settings_frame, text="Delay (seconds):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.delay_entry = ttk.Entry(settings_frame)
        self.delay_entry.insert(0, str(self.delay))
        self.delay_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Button(settings_frame, text="Update Settings", command=self.update_settings).grid(row=2, column=0, columnspan=2, pady=10)

    def create_video_list_frame(self):
        video_frame = ttk.LabelFrame(self, text="Detected Videos")
        video_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.video_listbox = tk.Listbox(video_frame)
        self.video_listbox.pack(padx=5, pady=5, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(video_frame, orient="vertical", command=self.video_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        self.video_listbox.config(yscrollcommand=scrollbar.set)

    def update_settings(self):
        try:
            new_delay = float(self.delay_entry.get())
            if new_delay < 0:
                raise ValueError("Delay must be non-negative")
            self.delay = new_delay
            self.event_handler.delay = new_delay
            messagebox.showinfo("Success", "Settings updated successfully")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid delay value: {str(e)}")

    def start_watching(self):
        self.event_handler = VideoHandler(self.delay, self.add_video_to_list)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.hot_folder, recursive=False)
        self.observer.start()

    def add_video_to_list(self, video_info):
        self.video_listbox.insert(tk.END, video_info)
        self.video_listbox.see(tk.END)  # Auto-scroll to the latest entry

    def on_closing(self):
        self.observer.stop()
        self.observer.join()
        self.destroy()

if __name__ == "__main__":
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()