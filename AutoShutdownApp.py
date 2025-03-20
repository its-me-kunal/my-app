import os
import time
import threading
import ctypes
import tkinter as tk
from tkinter import ttk
import sys
import pystray
from pystray import MenuItem as item, Icon, Menu
from PIL import Image, ImageDraw
from ttkthemes import ThemedStyle

# Developed by Mr.Kunal

class AutoShutdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Shutdown Monitor")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        self.root.configure(bg="#2C3E50")  

        self.running = False
        self.idle_threshold = 1800  
        self.current_idle_time = 0

        
        style = ThemedStyle(root)
        style.set_theme("arc")

        
        self.status_var = tk.StringVar(value="Monitoring Stopped")
        self.label = ttk.Label(root, textvariable=self.status_var, font=("Arial", 12, "bold"), background="#2C3E50", foreground="white")
        self.label.pack(pady=10)

        self.timer_label = ttk.Label(root, text="Idle Time: 0s", font=("Arial", 10), background="#2C3E50", foreground="white")
        self.timer_label.pack(pady=5)

        self.progress = ttk.Progressbar(root, length=250, mode='determinate', orient='horizontal')
        self.progress.pack(pady=5)

        self.threshold_label = ttk.Label(root, text="Shutdown after (mins):", font=("Arial", 10), background="#2C3E50", foreground="white")
        self.threshold_label.pack(pady=5)

        self.threshold_entry = ttk.Entry(root, width=10, justify='center', font=("Arial", 10))
        self.threshold_entry.pack(pady=5)
        self.threshold_entry.insert(0, "30") 

        self.start_button = ttk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(root, text="Stop Monitoring", command=self.stop_monitoring)
        self.stop_button.pack(pady=5)

        self.exit_button = ttk.Button(root, text="Minimize to Tray", command=self.minimize_to_tray)
        self.exit_button.pack(pady=10)

        self.developer_label = ttk.Label(root, text="Developed by Mr.Kunal", font=("Arial", 9), background="#2C3E50", foreground="white")
        self.developer_label.pack(side="bottom", pady=5)

    def get_idle_time(self):
        """Returns system idle time in seconds (Windows only)."""
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)

        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
            millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
            return millis // 1000  

        return 0

    def force_shutdown(self):
        """Force shutdown the system without user interaction."""
        if os.name == "nt":
            os.system("shutdown /s /f /t 0")  
        else:
            os.system("shutdown -h now")  

    def monitor_idle_time(self):
        while self.running:
            try:
                self.idle_threshold = int(self.threshold_entry.get()) * 60  
            except ValueError:
                self.idle_threshold = 1800  

            self.current_idle_time = self.get_idle_time()
            self.timer_label.config(text=f"Idle Time: {self.current_idle_time}s")
            
            progress_percentage = (self.current_idle_time / self.idle_threshold) * 100
            self.progress["value"] = progress_percentage

            if self.current_idle_time >= self.idle_threshold:
                self.force_shutdown()  
                break  

            time.sleep(5)  

    def start_monitoring(self):
        if not self.running:
            self.running = True
            self.status_var.set("Monitoring Active")
            self.monitor_thread = threading.Thread(target=self.monitor_idle_time)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

    def stop_monitoring(self):
        self.running = False
        self.status_var.set("Monitoring Stopped")
        self.progress['value'] = 0

    def minimize_to_tray(self):
        """Minimizes the app to the system tray."""
        self.root.withdraw()
        icon_image = Image.new('RGB', (64, 64), (255, 0, 0))
        draw = ImageDraw.Draw(icon_image)
        draw.rectangle([10, 10, 54, 54], fill=(0, 0, 255))
        menu = Menu(item("Exit", self.exit_app))
        self.tray_icon = Icon("AutoShutdown", icon_image, menu=menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def exit_app(self, icon, item):
        self.tray_icon.stop()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoShutdownApp(root)
    root.mainloop()
