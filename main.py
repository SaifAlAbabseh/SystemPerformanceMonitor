import tkinter as tk
from tkinter import font
import metrics

class SystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor - Pro Dashboard")
        self.root.configure(bg="#0b0c0f") # Ultra dark theme
        self.root.geometry("450x800")
        
        # Load fonts gracefully if not installed
        family = "Segoe UI Variable Display" if "Segoe UI Variable Display" in font.families() else "Segoe UI"
        
        self.header_font = font.Font(family=family, size=15, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=11)
        self.value_font = font.Font(family="Consolas", size=13, weight="bold")
        
        # Dashboard Palette
        self.bg_color = "#0b0c0f"
        self.card_color = "#15171e"
        self.text_color = "#a0a5b5"
        self.accent_color = "#4f9bff" # Modern Blue! (Looks much better than default orange, but we can change back)
        self.title_color = "#ffffff"
        
        # Keep Original Orange specifically for the user's implicit preference
        self.accent_color = "#FFB300"
        
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Creating Dashboard Cards
        self.cpu_card = self.create_card("CPU")
        self.cpu_usage_label = self.create_metric_row(self.cpu_card, "Active Load:", "0 %")
        self.cpu_temp_label = self.create_metric_row(self.cpu_card, "Temperature:", "0 °C")

        self.ram_card = self.create_card("RAM")
        self.ram_usage_label = self.create_metric_row(self.ram_card, "Active Load:", "0 %")
        self.ram_cap_label = self.create_metric_row(self.ram_card, "Capacity:", "0.0 / 0.0 GB")

        self.gpu_card = self.create_card("GPU")
        self.gpu_usage_label = self.create_metric_row(self.gpu_card, "Active Load:", "0 %")
        self.gpu_temp_label = self.create_metric_row(self.gpu_card, "Temperature:", "0 °C")
        self.gpu_vram_label = self.create_metric_row(self.gpu_card, "VRAM Usage:", "0.0 GB / 0.0 GB")

        self.disk_card = self.create_card("STORAGE (ACTIVE TIME)")
        self.disk_labels = {}
        
        if not metrics.is_admin():
            admin_warning = tk.Label(self.main_container, text="[!] Re-open App as Administrator to read CPU temps", bg=self.bg_color, fg="#ff6b6b", font=("Segoe UI", 10))
            admin_warning.pack(pady=10)

        self.update_metrics()

    def create_card(self, title):
        card = tk.Frame(self.main_container, bg=self.card_color)
        card.pack(fill="x", pady=8)
        
        # Card Header
        header_frame = tk.Frame(card, bg=self.card_color)
        header_frame.pack(fill="x", padx=15, pady=(12, 0))
        tk.Label(header_frame, text=title, bg=self.card_color, fg=self.title_color, font=self.header_font).pack(side="left")
        
        # Separator line inside card
        sep = tk.Frame(card, bg="#2d313a", height=1)
        sep.pack(fill="x", padx=15, pady=(8, 5))
        
        # Metric content container
        content = tk.Frame(card, bg=self.card_color)
        content.pack(fill="x", padx=15, pady=(5, 12))
        return content

    def create_metric_row(self, parent, label_text, default_value):
        row = tk.Frame(parent, bg=self.card_color)
        row.pack(fill="x", pady=4)
        
        tk.Label(row, text=label_text, bg=self.card_color, fg=self.text_color, font=self.label_font, width=15, anchor="w").pack(side="left")
        
        value_label = tk.Label(row, text=default_value, bg=self.card_color, fg=self.accent_color, font=self.value_font)
        value_label.pack(side="right")
        return value_label

    def update_metrics(self):
        # Update CPU
        cpu_usage = metrics.get_cpu_utilization()
        cpu_temp = metrics.get_cpu_temperature()
        self.cpu_usage_label.config(text=f"{cpu_usage} %")
        self.cpu_temp_label.config(text=f"{cpu_temp} °C" if cpu_temp != "N/A" else "N/A")

        # Update RAM
        ram_info = metrics.get_ram_info()
        self.ram_usage_label.config(text=f"{ram_info['percent']} %")
        self.ram_cap_label.config(text=f"{ram_info['used']} GB / {ram_info['total']} GB")

        # Update GPU
        gpu_info = metrics.get_gpu_info()
        self.gpu_usage_label.config(text=f"{gpu_info['load']} %")
        self.gpu_temp_label.config(text=f"{gpu_info['temp']} °C" if getattr(gpu_info.get('temp'), 'real', 0) or gpu_info.get('temp') == 0 else "N/A")
        
        vram_used = gpu_info.get('vram_used', "N/A")
        vram_total = gpu_info.get('vram_total', "N/A")
        if vram_used != "N/A":
            self.gpu_vram_label.config(text=f"{vram_used} GB / {vram_total} GB")
        else:
            self.gpu_vram_label.config(text="N/A")

        # Update Disks
        disks = metrics.get_disk_info()
        
        for disk in disks:
            dev = disk['device']
            if dev not in self.disk_labels:
                self.disk_labels[dev] = self.create_metric_row(self.disk_card, f"Disk {dev}", "0 %")
            
            # WMI active disk times sometimes spike > 100 on NVME drives momentarily 
            val = min(100, disk['percent'])
            self.disk_labels[dev].config(text=f"{val} %")

        self.root.after(1500, self.update_metrics)

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.mainloop()

