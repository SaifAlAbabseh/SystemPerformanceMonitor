import psutil
import subprocess
import os

# Prevent GPUtil (nvidia-smi subprocess) from flashing a CMD window every second
if os.name == 'nt':
    original_popen = subprocess.Popen
    def _popen_no_console(*args, **kwargs):
        kwargs['creationflags'] = 0x08000000 # CREATE_NO_WINDOW
        return original_popen(*args, **kwargs)
    subprocess.Popen = _popen_no_console

import GPUtil
import wmi
import clr
import os
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

import sys

def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

# Initialize Global LibreHardwareMonitor instance for accurate hardware temps
computer = None
try:
    dll_path = os.path.join(get_base_path(), 'LibreHardwareMonitorLib.dll')
    clr.AddReference(dll_path)
    from LibreHardwareMonitor import Hardware
    computer = Hardware.Computer()
    computer.IsCpuEnabled = True
    computer.Open()
except Exception:
    pass

try:
    c = wmi.WMI()
except Exception:
    c = None

def get_cpu_utilization():
    return psutil.cpu_percent(interval=None)

def get_cpu_temperature():
    if computer:
        try:
            for hw in computer.Hardware:
                if hw.HardwareType == Hardware.HardwareType.Cpu:
                    hw.Update()
                    # The CPU often has many sensors. We filter for Package or Core Average
                    for sensor in hw.Sensors:
                        if sensor.SensorType == Hardware.SensorType.Temperature:
                            if 'CPU Package' in sensor.Name or 'Core Average' in sensor.Name or 'Tdie' in sensor.Name or 'CPU' in sensor.Name:
                                return round(sensor.Value)
        except Exception:
            pass
    return "N/A"

def get_ram_info():
    mem = psutil.virtual_memory()
    return {
        "percent": mem.percent,
        "used": round(mem.used / (1024**3), 1),
        "total": round(mem.total / (1024**3), 1)
    }

def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            return {
                "load": round(gpu.load * 100),
                "temp": round(gpu.temperature),
                "vram_used": round(gpu.memoryUsed / 1024, 1),
                "vram_total": round(gpu.memoryTotal / 1024, 1)
            }
    except Exception:
        pass
    return {"load": "N/A", "temp": "N/A", "vram_used": "N/A", "vram_total": "N/A"}

def get_disk_info():
    disks = []
    if c:
        try:
            # Native WMI class returns actual active time %, not storage capacities!
            for disk in c.Win32_PerfFormattedData_PerfDisk_PhysicalDisk():
                if disk.Name != "_Total":
                    disks.append({
                        "device": disk.Name,
                        "percent": int(disk.PercentDiskTime)
                    })
        except Exception:
            pass
    return disks
