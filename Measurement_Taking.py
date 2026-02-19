import eyes17.eyes
import threading
import time
import csv 
import os 
import numpy as np

Date='27_01' 
try_no=270101

channel_thermocouple="A2"
channel_strain="A1"
sample_interval=2


file_path=r"C:\Users\Rajat\Downloads\Strain_Data_Measurement_heating_1002.csv"
#file_path=r"C:\Users\Rajat\Downloads\Strain_Data_Measurement_cooling_1002.csv"

os. makedirs (os. path . dirname ( file_path ), exist_ok = True )

V_STOP=3.0


if not os.path.exists(output_filename):
    with open(output_filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Time (s)",
            f"Voltage_{channel_thermocouple} (V)",
            f"Voltage_{channel_strain} (V)"
        ])

# Connect to device
seelab = eyes17.eyes.open()

# Data storage
data = []
running = True

# ---------------- ACQUISITION FUNCTION ----------------
def collect_data():
    global running
    start_time = time.time()

    while running:
        t = time.time() - start_time

        try:
            v_thermo = seelab.get_voltage(channel_thermocouple)
            v_strain = (-1)*seelab.get_voltage(channel_strain)
        except KeyError:
            print("Error: Invalid analog channel. Check connections.")
            running = False
            break

        data.append((t, v_thermo, v_strain))

        print(f"t = {t:.1f} s | Thermo = {v_thermo:.3f} V | Strain = {v_strain:.3f} V")

        # ---- AUTO STOP CONDITION ----
        if v_thermo >= V_STOP:
            print(f"\nThermocouple reached {V_STOP} V. Stopping acquisition.\n")
            running = False
            break
        # -----------------------------

        time.sleep(sample_interval)

# Start acquisition in a separate thread
acq_thread = threading.Thread(target=collect_data)
acq_thread.start()

# Manual stop option
input(f"\nCollecting data... Press Enter to stop manually.\nSaving to:\n{output_filename}\n")

running = False
acq_thread.join()

# ---------------- SAVE DATA ----------------
with open(output_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        "Time (s)",
        f"Voltage_{channel_thermocouple} (V)",
        f"Voltage_{-1*channel_strain} (V)"
    ])
    writer.writerows(data)

# seelab.close()   # optional


print(f"\nData saved to '{output_filename}' with {len(data)} samples.")

