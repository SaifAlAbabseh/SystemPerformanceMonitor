import wmi
import clr
import os

print("--- Disks ---")
try:
    c = wmi.WMI()
    
    # You MUST use Win32_PerfFormattedData for PercentDiskTime, RawData gives useless raw ticks.
    for disk in c.Win32_PerfFormattedData_PerfDisk_PhysicalDisk():
        if disk.Name != "_Total":
            print(f"Disk: {disk.Name}, Active Time: {disk.PercentDiskTime}%")
except Exception as e:
    print(f"WMI Disk Error: {e}")

print("--- CPU Temp via DLL ---")
try:
    dll_path = os.path.abspath('LibreHardwareMonitorLib.dll')
    clr.AddReference(dll_path)
    from LibreHardwareMonitor import Hardware
    
    computer = Hardware.Computer()
    computer.IsCpuEnabled = True
    computer.Open()
    
    for hw in computer.Hardware:
        if hw.HardwareType == Hardware.HardwareType.Cpu:
            hw.Update()
            for sensor in hw.Sensors:
                if sensor.SensorType == Hardware.SensorType.Temperature:
                    if 'CPU Package' in sensor.Name or 'Core Average' in sensor.Name or 'CCD' in sensor.Name or 'Core' in sensor.Name:
                        print(f"{sensor.Name}: {sensor.Value} C")
except Exception as e:
    print(f"DLL Error: {e}")

