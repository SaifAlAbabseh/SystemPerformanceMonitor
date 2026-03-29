import psutil
import time
import wmi

# RAM
ram = psutil.virtual_memory()
print(f"RAM Usage: {ram.percent}%")

# Disk active time
def test_disk_active():
    t1 = time.time()
    io1 = psutil.disk_io_counters(perdisk=True)
    time.sleep(1)
    t2 = time.time()
    io2 = psutil.disk_io_counters(perdisk=True)
    
    for disk, counters in io2.items():
        if disk in io1:
            read_time_diff = counters.read_time - io1[disk].read_time
            write_time_diff = counters.write_time - io1[disk].write_time
            total_active_time = (read_time_diff + write_time_diff) # in ms
            time_elapsed = (t2 - t1) * 1000 # in ms
            percent = min(100.0, (total_active_time / time_elapsed) * 100)
            print(f"Disk {disk} Active Time: {percent:.1f}%")

test_disk_active()

# CPU temp alternative using wmi
try:
    w = wmi.WMI(namespace="root\\cimv2")
    temperature_info = w.query("SELECT * FROM Win32_TemperatureProbe")
    if temperature_info:
        for entry in temperature_info:
            print(f"Win32_TemperatureProbe: {entry.CurrentReading}")
    else:
        print("Win32_TemperatureProbe returned empty")
except Exception as e:
    print(f"Win32_TemperatureProbe Error: {e}")

try:
    t = wmi.WMI(namespace="root\\OpenHardwareMonitor")
    hw = t.Sensor()
    for sensor in hw:
        if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
            print(f"OHM Temp: {sensor.Value}")
except Exception as e:
    print(f"OHM Error: {e}")

try:
    import psutil
    print(f"psutil sensors: {psutil.sensors_temperatures()}")
except Exception as e:
    pass

