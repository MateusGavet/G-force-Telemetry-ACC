# Telemetry Reader for Assetto Corsa Competizione

A project with a graphical user interface (GUI), CSV data logging, and a long debugging journey to reach the final solution. This reader displays G-Force in real time and saves the entire session history for later analysis.

![Window Example](https://iili.io/KWx7YXI.png)

## Summary

The initial goal was simple: create a Python script to read G-Force from Assetto Corsa Competizione (ACC) and display it in the terminal. However, due to a series of compatibility challenges with external libraries and the user's Python version (3.11), the project evolved into a robust, dependency-free solution using only Python's native modules.

This repository contains the final, functional code, along with documentation of the entire development and debugging journey.

## Features

-   **Real-Time Display:** Shows G-Force data (Lateral, Longitudinal, and Vertical) in real time.
-   **Graphical User Interface (GUI):** Uses the native `Tkinter` library to create an easy-to-read window.
-   **Complete Data Logging:** Saves the entire session's telemetry history (with timestamps) to a `.csv` file, ready to be analyzed in Excel, Google Sheets, etc.
-   **No External Dependencies:** The final version does not require installing any libraries via `pip`, ensuring maximum compatibility.
-   **Automatic Connection:** Detects when the game is in a session and attempts to reconnect if the game is closed and reopened.

## Requirements

-   Assetto Corsa Competizione
-   Python 3.7 or higher (developed and tested on Python 3.11)

## Setup (One-Time Step)

Before running the script, you need to enable "Shared Memory" in ACC.

1.  Go to your game's configuration folder. Usually located at:
    `C:\Users\[Your Name]\Documents\Assetto Corsa Competizione\Config`
2.  Open the `broadcasting.json` file with a text editor.
3.  Find the line `"enableSharedMemory": 0` and change the `0` to `1`.
4.  Save the file. Your file should now contain the following line:
    ```json
    {
      ...
      "enableSharedMemory": 1,
      ...
    }
    ```

## How to Use

1.  Save the final code below into a file named `acc_reader.py`.
2.  Start Assetto Corsa Competizione and enter a session (go on track).
3.  Open a terminal (CMD, PowerShell, etc.) in the folder where you saved the file and run the command:
    ```bash
    python acc_reader.py
    ```
4.  A window will appear, showing the G-Force data. In the same folder, a file named `acc_log_ctypes_DATE_TIME.csv` will be created and will start recording the data.
5.  To stop, simply close the window. The CSV file will be saved safely.

---

## The Final Code

This is the final and 100% functional script, which we achieved after the entire debugging process.

```python
# Python Imports
import ctypes
import mmap
import time
import os
import sys
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont

# DATA STRUCTURE DEFINITION (The manual method that WORKED)
class SPageFilePhysics(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('packetId', ctypes.c_int),
        ('gas', ctypes.c_float),
        ('brake', ctypes.c_float),
        ('fuel', ctypes.c_float),
        ('gear', ctypes.c_int),
        ('rpms', ctypes.c_int),
        ('steerAngle', ctypes.c_float),
        ('speedKmh', ctypes.c_float),
        ('velocity', ctypes.c_float * 3),
        ('accG', ctypes.c_float * 3),
        ('wheelSlip', ctypes.c_float * 4),
        ('wheelLoad', ctypes.c_float * 4),
        ('wheelsPressure', ctypes.c_float * 4),
        ('wheelAngularSpeed', ctypes.c_float * 4),
        ('tyreWear', ctypes.c_float * 4),
        ('tyreDirtyLevel', ctypes.c_float * 4),
        ('tyreCoreTemperature', ctypes.c_float * 4),
        ('camberRAD', ctypes.c_float * 4),
        ('suspensionTravel', ctypes.c_float * 4),
        ('drs', ctypes.c_float),
        ('tc', ctypes.c_float),
        ('heading', ctypes.c_float),
        ('pitch', ctypes.c_float),
        ('roll', ctypes.c_float),
        ('cgHeight', ctypes.c_float),
        ('carDamage', ctypes.c_float * 5),
        ('numberOfTyresOut', ctypes.c_int),
        ('pitLimiterOn', ctypes.c_int),
        ('abs', ctypes.c_float),
        ('kersCharge', ctypes.c_float),
        ('kersInput', ctypes.c_float),
        ('autoShifterOn', ctypes.c_int),
        ('rideHeight', ctypes.c_float * 2),
        ('turboBoost', ctypes.c_float),
        ('ballast', ctypes.c_float),
        ('airDensity', ctypes.c_float),
        ('airTemp', ctypes.c_float),
        ('roadTemp', ctypes.c_float),
        ('localAngularVel', ctypes.c_float * 3),
        ('finalFF', ctypes.c_float),
        ('performanceMeter', ctypes.c_float),
        ('engineBrake', ctypes.c_int),
        ('ersRecoveryLevel', ctypes.c_int),
        ('ersPowerLevel', ctypes.c_int),
        ('ersHeatCharging', ctypes.c_int),
        ('ersIsCharging', ctypes.c_int),
        ('kersCurrentKJ', ctypes.c_float),
        ('drsAvailable', ctypes.c_int),
        ('drsEnabled', ctypes.c_int),
        ('brakeTemp', ctypes.c_float * 4),
        ('clutch', ctypes.c_float),
        ('tyreTempI', ctypes.c_float * 4),
        ('tyreTempM', ctypes.c_float * 4),
        ('tyreTempO', ctypes.c_float * 4),
        ('isAIControlled', ctypes.c_int),
        ('tyreContactPoint', ctypes.c_float * 4 * 3),
        ('tyreContactNormal', ctypes.c_float * 4 * 3),
        ('tyreContactHeading', ctypes.c_float * 4 * 3),
        ('brakeBias', ctypes.c_float),
        ('localVelocity', ctypes.c_float * 3),
        ('P2PActivations', ctypes.c_int),
        ('P2PStatus', ctypes.c_int),
        ('currentMaxRpm', ctypes.c_int),
        ('mz', ctypes.c_float * 4),
        ('fx', ctypes.c_float * 4),
        ('fy', ctypes.c_float * 4),
        ('slipRatio', ctypes.c_float * 4),
        ('slipAngle', ctypes.c_float * 4),
        ('tcinAction', ctypes.c_int),
        ('absInAction', ctypes.c_int),
        ('suspensionDamage', ctypes.c_float * 4),
        ('tyreTemp', ctypes.c_float * 4),
        ('waterTemp', ctypes.c_float),
        ('brakePressure', ctypes.c_float * 4),
        ('frontBrakeCompound', ctypes.c_int),
        ('rearBrakeCompound', ctypes.c_int),
        ('padLife', ctypes.c_float * 4),
        ('discLife', ctypes.c_float * 4),
        ('ignitionOn', ctypes.c_int),
        ('starterEngineOn', ctypes.c_int),
        ('isEngineRunning', ctypes.c_int),
        ('kerbVibration', ctypes.c_float),
        ('slipVibrations', ctypes.c_float),
        ('gVibrations', ctypes.c_float),
        ('absVibrations', ctypes.c_float),
    ]

# MAIN APPLICATION CLASS (ctypes version)
class TelemetryApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("ACC Telemetry - G-Force (v. Ctypes)")
        self.root.geometry("350x200")
        
        self.shm = None
        self.csv_file = None
        self.csv_writer = None
        self.last_packet_id = -1
        
        self.data_font = tkFont.Font(family="Consolas", size=14, weight="bold")
        self.label_font = tkFont.Font(family="Arial", size=10)
        
        self.g_lat_var = tk.StringVar(value="-- G")
        self.g_lon_var = tk.StringVar(value="-- G")
        self.g_ver_var = tk.StringVar(value="-- G")
        self.status_var = tk.StringVar(value="Initializing...")

        self.setup_gui()
        self.setup_csv()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_gui(self):
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
        style.configure("Data.TLabel", font=self.data_font, foreground="#003366")
        style.configure("Header.TLabel", font=self.label_font, foreground="#333333")
        style.configure("Status.TLabel", font=self.label_font, foreground="#555555")

        frame = ttk.Frame(self.root, padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Lateral G-Force (Turns):", style="Header.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame, text="Long. G-Force (Brake/Accel.):", style="Header.TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame, text="Vertical G-Force (Kerbs):", style="Header.TLabel").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame, textvariable=self.g_lat_var, style="Data.TLabel").grid(row=0, column=1, sticky=tk.E, padx=10)
        ttk.Label(frame, textvariable=self.g_lon_var, style="Data.TLabel").grid(row=1, column=1, sticky=tk.E, padx=10)
        ttk.Label(frame, textvariable=self.g_ver_var, style="Data.TLabel").grid(row=2, column=1, sticky=tk.E, padx=10)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=10)
        ttk.Label(frame, textvariable=self.status_var, style="Status.TLabel").grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5)
        frame.columnconfigure(1, weight=1)

    def setup_csv(self):
        try:
            filename = f"acc_log_ctypes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.csv_file = open(filename, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(["Timestamp", "PacketID", "G_Lateral", "G_Longitudinal", "G_Vertical"])
            print(f"Saving log to: {filename}")
        except IOError as e:
            print(f"Error creating CSV file: {e}")
            self.status_var.set("Error creating CSV!")

    def update_data(self):
        try:
            if self.shm is None:
                try:
                    self.shm = mmap.mmap(0, ctypes.sizeof(SPageFilePhysics), "acpmf_physics", mmap.ACCESS_READ)
                except FileNotFoundError:
                    self.status_var.set("Waiting for ACC... (Check broadcasting.json)")
                    self.root.after(1000, self.update_data)
                    return
            
            self.shm.seek(0)
            buffer = self.shm.read(ctypes.sizeof(SPageFilePhysics))
            physics_data = SPageFilePhysics.from_buffer_copy(buffer)

            current_packet_id = physics_data.packetId
            if current_packet_id == 0 or current_packet_id == self.last_packet_id:
                if current_packet_id == 0:
                    self.status_var.set("Connected. Waiting on track...")
                self.root.after(16, self.update_data)
                return
            
            self.last_packet_id = current_packet_id
            self.status_var.set("Connected! Reading data...")

            g_lat = physics_data.accG[0]
            g_lon = physics_data.accG[2]
            g_ver = physics_data.accG[1]

            self.g_lat_var.set(f"{g_lat: 8.3f} G")
            self.g_lon_var.set(f"{g_lon: 8.3f} G")
            self.g_ver_var.set(f"{g_ver: 8.3f} G")

            if self.csv_writer:
                timestamp = datetime.now().isoformat()
                self.csv_writer.writerow([timestamp, current_packet_id, g_lat, g_lon, g_ver])

        except Exception as e:
            print(f"Error in update loop: {e}")
            if isinstance(e, FileNotFoundError):
                self.shm = None
                self.status_var.set("Game disconnected. Attempting to reconnect...")
            time.sleep(1)

        self.root.after(16, self.update_data)

    def on_close(self):
        print("Closing... Saving CSV file.")
        
        if self.csv_file:
            self.csv_file.close()
            print("CSV file saved successfully.")
            
        if self.shm:
            self.shm.close()
            
        self.root.destroy()

# MAIN EXECUTION BLOCK
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = TelemetryApp(root)
        
        root.after(16, app.update_data)
        
        root.mainloop()
        
    except Exception as e:
        print(f"A fatal error occurred: {e}")
    finally:
        print("Program terminated.")
```

---

## The Development Journey (Debug Logs)

The creation of this script was an iterative process, filled with challenges that are common in software development.

### Phase 1: The Initial Request - Terminal Reader

The goal was simple: read G-Force from ACC and display it in the terminal. The initial approach was to use an external library to facilitate reading the game's shared memory.

### Phase 2: The First Challenge - Libraries vs. Python 3.11

The first attempt was to use the `sim_info` library. The command `pip install sim-info` failed immediately.

-   **Diagnosis:** We discovered that the user was on Python 3.11, a very recent version for which the library did not have pre-compiled files ("wheels"). The installation would have required a C++ compiler (Microsoft C++ Build Tools), which was an overly complex dependency.
-   **Solution:** We decided to abandon external libraries and build a "manual" reader, using Python's native modules `ctypes` (to read C-style data structures) and `mmap` (to map the shared memory).

### Phase 3: The Manual Method (`ctypes`) and Initial Success

A script was provided that recreated the ACC physics data structure in Python and read it directly from memory. After fixing a few bugs (`AttributeError: 'mmap' object has no attribute 'read_into'` and `NameError: name 'mmap' is not defined`), we arrived at a functional version that displayed the data in the terminal. **This was the first major victory**.

### Phase 4: Evolution - Graphical Interface (Tkinter) and CSV Logging

With the data reading logic validated, a graphical window and CSV history logging were added. A new script was created that encapsulated the functional `ctypes` logic within a `Tkinter` application class.

### Phase 5: The "Dead End" of Libraries

Before testing the `ctypes` version with Tkinter, we tried again to use a library, this time `pyaccsharedmemory`. This led us down a long and confusing debugging path:

1.  The `pip install pyaccsharedmemory` installation worked, which led us to believe the user had the necessary C++ build tools.
2.  My attempts to use the library failed, as I was guessing the class and method names (`ACSharedMemory`, `read_physics`, etc.).
3.  We tried with another script (an AI environment with `gymnasium`) that successfully used the library. This script was our "Rosetta Stone," revealing the correct names: `accSharedMemory` and `read_shared_memory`.
4.  Even with the correct names, the script continued to fail with an `AttributeError`, as the library did not seem to have the attributes we needed (`packetId`, `accG`).

**Conclusion of Phase 5:** The `pyaccsharedmemory` library, on the user's machine, was somehow incomplete, broken, or inconsistent, not exposing all the necessary data.

### Phase 6: The Final Solution - Returning to `ctypes`

It became clear that the library path was a dead end. The most robust and reliable solution was to return to the method we had already proven to work.

The final version of the script is, therefore, the one that combines the **functional `ctypes` logic** from Phase 3 with the **Tkinter interface and CSV logging** from Phase 4. This final version has no external dependencies and is tailored to work perfectly in the user's environment.

## Conclusion

This project is an excellent example of a real-world problem: what seems like a simple task can become complex due to dependency and compatibility issues. The final solution, although more verbose, is superior because it is self-contained and more resilient to environment-related problems.

## License

```
MIT License

Copyright (c) 2025 Mateus Gavet

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
