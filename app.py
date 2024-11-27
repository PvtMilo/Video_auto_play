import os
import sys
import time
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
from datetime import datetime
from PIL import Image, ImageTk
import threading

CONFIG_FILE = "video_player_config.json"
custom_title = "Wolfie_AV_Player"

def create_ico_from_png(png_path, ico_path):
    """Convert PNG to ICO format for Windows"""
    try:
        img = Image.open(png_path)
        icon_sizes = [(16,16), (32, 32), (48,48), (64,64)]
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        return True
    except Exception as e:
        print(f"Failed to convert PNG to ICO: {e}")
        return False

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"hot_folder": os.path.expanduser("~")}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

class VideoHandler(FileSystemEventHandler):
    def __init__(self, delay, callback):
        self.delay = delay
        self.callback = callback
        self.is_paused = False
        self.is_running = True

    def on_created(self, event):
        if not self.is_paused and not event.is_directory and self.is_running and event.src_path.lower().endswith(('.mp4', '.avi', '.mkv')):
            video_name = os.path.basename(event.src_path)
            detection_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.callback(f"{detection_time} - {video_name}")
            print(f"New video detected: {event.src_path}")
            time.sleep(self.delay)
            self.play_video(event.src_path)

    def play_video(self, video_path):
        try:
            os.startfile(video_path)
        except AttributeError:
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', video_path))
            else:
                subprocess.call(('xdg-open', video_path))

    def stop(self):
        self.is_running = False

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Prevent multiple instances
        self.instance_check()
        
        # Set custom icon
        self.set_app_icon()
        
        self.title(custom_title)
        
        # Set window size
        window_width = 500
        window_height = 500
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate center position
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        # Set window size and position
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Prevent window resizing below minimum size
        self.minsize(300, 200)
        
        self.configure(bg='#f0f0f0')
        
        # Load saved configuration
        config = load_config()
        self.hot_folder = config["hot_folder"]
        self.delay = 5
        self.video_count = 0
        self.is_watching = True
        
        # Observer management
        self.observer = None
        self.event_handler = None

        # Configure the style
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Configure colors
        bg_color = '#f0f0f0'
        self.style.configure('Custom.TFrame', background=bg_color)
        self.style.configure('Custom.TLabelframe', background=bg_color)
        self.style.configure('Custom.TLabelframe.Label', background=bg_color, font=('Segoe UI', 10, 'bold'))
        self.style.configure('Custom.TButton', font=('Segoe UI', 9))
        self.style.configure('StatusButton.TButton', padding=5)
        self.style.configure('Header.TLabel', background=bg_color, font=('Segoe UI', 14, 'bold'))
        self.style.configure('Info.TLabel', background=bg_color, font=('Segoe UI', 9))
        
        self.create_widgets()
        self.start_watching()
        
        # Ensure proper cleanup on exit
        self.protocol("WM_DELETE_WINDOW", self.safe_exit)

    def instance_check(self):
        """Prevent multiple instances of the application"""
        try:
            import socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('localhost', 0))
            self.socket.listen(1)
        except Exception:
            messagebox.showerror("Error", "Another instance of the application is already running.")
            sys.exit(1)

    def set_app_icon(self):
        try:
            icon_path = 'icon.png'  # Make sure your icon.png is in the same directory
            
            if sys.platform.startswith('win'):
                # For Windows
                ico_path = icon_path.replace('.png', '.ico')
                if not os.path.exists(ico_path):
                    create_ico_from_png(icon_path, ico_path)
                self.iconbitmap(ico_path)
            else:
                # For Linux/Unix/Mac
                img = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, img)
                
        except Exception as e:
            print(f"Failed to set application icon: {e}")

    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self, style='Custom.TFrame', padding="20")
        main_frame.pack(fill='both', expand=True)

        # Top section
        top_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        top_frame.pack(fill='x', pady=(0, 20))

        # Title and status indicator in the same row
        title_frame = ttk.Frame(top_frame, style='Custom.TFrame')
        title_frame.pack(fill='x')

        title_label = ttk.Label(title_frame, text=custom_title, style='Header.TLabel')
        title_label.pack(side='left')

        # Status indicators and control buttons
        self.status_frame = ttk.Frame(title_frame, style='Custom.TFrame')
        self.status_frame.pack(side='right')

        self.status_label = ttk.Label(self.status_frame, text="●", font=('Segoe UI', 14), foreground='green')
        self.status_label.pack(side='left', padx=5)

        self.toggle_button = ttk.Button(self.status_frame, text="Pause", 
                                      style='StatusButton.TButton', 
                                      command=self.toggle_watching)
        self.toggle_button.pack(side='left', padx=5)

        self.create_settings_frame(main_frame)
        self.create_video_list_frame(main_frame)

    def create_settings_frame(self, parent):
        settings_frame = ttk.LabelFrame(parent, text="Settings", style='Custom.TLabelframe', padding="15")
        settings_frame.pack(fill='x', padx=5, pady=(0, 15))

        # Grid layout for better organization
        settings_frame.columnconfigure(1, weight=1)

        # Folder selection
        ttk.Label(settings_frame, text="Watch Folder:", style='Info.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.folder_label = ttk.Label(settings_frame, text=self.hot_folder, style='Info.TLabel', wraplength=500)
        self.folder_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        browse_btn = ttk.Button(settings_frame, text="Browse", style='Custom.TButton', command=self.browse_folder)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)

        # Delay settings
        ttk.Label(settings_frame, text="Delay (seconds):", style='Info.TLabel').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.delay_entry = ttk.Entry(settings_frame, width=10)
        self.delay_entry.insert(0, str(self.delay))
        self.delay_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        update_btn = ttk.Button(settings_frame, text="Update Delay", style='Custom.TButton', command=self.update_settings)
        update_btn.grid(row=1, column=2, padx=5, pady=5)

    def create_video_list_frame(self, parent):
        video_frame = ttk.LabelFrame(parent, text="Activity Log", style='Custom.TLabelframe', padding="15")
        video_frame.pack(fill='both', expand=True, padx=5)

        # Info bar
        info_frame = ttk.Frame(video_frame, style='Custom.TFrame')
        info_frame.pack(fill='x', pady=(0, 10))

        self.count_label = ttk.Label(info_frame, text="Videos Detected: 0", style='Info.TLabel')
        self.count_label.pack(side='left')

        clear_btn = ttk.Button(info_frame, text="Clear Log", style='Custom.TButton', 
                             command=self.clear_log)
        clear_btn.pack(side='right')

        # Custom text widget for log
        self.video_log = tk.Text(video_frame, 
                                wrap=tk.WORD,
                                font=('Consolas', 10),
                                bg='white',
                                fg='#333333',
                                borderwidth=1,
                                relief='solid',
                                height=10)
        self.video_log.pack(side='left', fill='both', expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(video_frame, orient="vertical", command=self.video_log.yview)
        scrollbar.pack(side='right', fill='y')
        self.video_log.config(yscrollcommand=scrollbar.set)
        
        # Make text widget read-only
        self.video_log.config(state='disabled')

    def toggle_watching(self):
        self.is_watching = not self.is_watching
        if self.is_watching:
            self.toggle_button.config(text="Pause")
            self.status_label.config(foreground='green')
            self.event_handler.is_paused = False
            self.add_video_to_list("Monitoring resumed")
        else:
            self.toggle_button.config(text="Start")
            self.status_label.config(foreground='red')
            self.event_handler.is_paused = True
            self.add_video_to_list("Monitoring paused")

    def clear_log(self):
        self.video_log.config(state='normal')
        self.video_log.delete(1.0, tk.END)
        self.video_log.config(state='disabled')
        self.video_count = 0
        self.count_label.config(text=f"Videos Detected: {self.video_count}")

    def add_video_to_list(self, video_info):
        self.video_log.config(state='normal')
        self.video_log.insert(tk.END, f"{video_info}\n")
        self.video_log.see(tk.END)
        self.video_log.config(state='disabled')
        
        if not video_info.startswith("Monitoring"):  # Don't count status messages
            self.video_count += 1
            self.count_label.config(text=f"Videos Detected: {self.video_count}")

    def browse_folder(self):
        new_folder = filedialog.askdirectory(initialdir=self.hot_folder)
        if new_folder:
            self.hot_folder = new_folder
            self.folder_label.config(text=self.hot_folder)
            save_config({"hot_folder": self.hot_folder})
            self.restart_observer()

    def restart_observer(self):
        self.observer.stop()
        self.observer.join()
        self.start_watching()
        messagebox.showinfo("Success", "Watch folder updated successfully")

    def update_settings(self):
        try:
            new_delay = float(self.delay_entry.get())
            if new_delay < 0:
                raise ValueError("Delay must be non-negative")
            self.delay = new_delay
            self.event_handler.delay = new_delay
            messagebox.showinfo("Success", "Delay updated successfully")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid delay value: {str(e)}")

    def start_watching(self):
        """Start the file watching process with improved error handling"""
        try:
            # Stop any existing observer
            if self.observer:
                self.stop_watching()
            
            self.event_handler = VideoHandler(self.delay, self.add_video_to_list)
            self.observer = Observer()
            self.observer.schedule(self.event_handler, self.hot_folder, recursive=False)
            
            # Use a daemon thread for the observer to ensure it can be stopped
            observer_thread = threading.Thread(target=self.observer.start, daemon=True)
            observer_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start watching folder: {str(e)}")

    def stop_watching(self):
        """Safely stop the file watching process"""
        try:
            if self.observer:
                self.event_handler.stop()
                self.observer.stop()
                self.observer.join(timeout=5)  # Wait for observer to stop
                self.observer = None
                self.event_handler = None
        except Exception as e:
            print(f"Error stopping observer: {e}")

    def safe_exit(self):
        """Safely exit the application"""
        try:
            # Stop watching
            self.stop_watching()
            
            # Save configuration
            save_config({"hot_folder": self.hot_folder})
            
            # Close the socket to release the instance lock
            if hasattr(self, 'socket'):
                self.socket.close()
            
            # Destroy the window
            self.destroy()
            
            # Exit the application
            sys.exit(0)
        except Exception as e:
            print(f"Error during exit: {e}")
            sys.exit(1)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to log unexpected errors"""
    import traceback
    # Log the error
    print("Uncaught exception:", exc_type.__name__, exc_value)
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    # Prevent the default error dialog
    sys.exit(1)

# Set the global exception handler
sys.excepthook = handle_exception

if __name__ == "__main__":
    try:
        app = Application()
        app.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
