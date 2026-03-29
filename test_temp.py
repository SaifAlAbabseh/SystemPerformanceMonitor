import wmi
try:
    w = wmi.WMI(namespace="root\\wmi")
    temperature_info = w.MSAcpi_ThermalZoneTemperature()
    for entry in temperature_info:
        temp_c = (entry.CurrentTemperature / 10.0) - 273.15
        print(f"WMI Temp: {temp_c} C")
except Exception as e:
    print(f"WMI Error: {e}")

try:
    import psutil
    print(psutil.sensors_temperatures())
except Exception as e:
    print(f"psutil Sensor Error: {e}")
