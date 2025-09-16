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

# Dados Obtdos
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
        ('accG', ctypes.c_float * 3),  # <-- Nossos dados!
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

class TelemetryApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Telemetria ACC - Força G")
        self.root.geometry("350x200") # Tamanho da janela
        
        self.shm = None
        self.csv_file = None
        self.csv_writer = None
        self.last_packet_id = -1
        
        self.data_font = tkFont.Font(family="Consolas", size=14, weight="bold")
        self.label_font = tkFont.Font(family="Arial", size=10)
        
        self.g_lat_var = tk.StringVar(value="-- G")
        self.g_lon_var = tk.StringVar(value="-- G")
        self.g_ver_var = tk.StringVar(value="-- G")
        self.status_var = tk.StringVar(value="Iniciando...")

        self.setup_gui()
        
        self.setup_csv()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_gui(self):
        """Cria os elementos visuais da janela."""
        
        # "beleza" da janela
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
        style.configure("Data.TLabel", font=self.data_font, foreground="#003366")
        style.configure("Header.TLabel", font=self.label_font, foreground="#333333")
        style.configure("Status.TLabel", font=self.label_font, foreground="#555555")

        frame = ttk.Frame(self.root, padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Força G Lateral (Curvas):", style="Header.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame, text="Força G Long. (Freio/Acel.):", style="Header.TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame, text="Força G Vertical (Zebras):", style="Header.TLabel").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, textvariable=self.g_lat_var, style="Data.TLabel").grid(row=0, column=1, sticky=tk.E, padx=10)
        ttk.Label(frame, textvariable=self.g_lon_var, style="Data.TLabel").grid(row=1, column=1, sticky=tk.E, padx=10)
        ttk.Label(frame, textvariable=self.g_ver_var, style="Data.TLabel").grid(row=2, column=1, sticky=tk.E, padx=10)
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=10)

        ttk.Label(frame, textvariable=self.status_var, style="Status.TLabel").grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5)

        frame.columnconfigure(1, weight=1) # Faz a coluna 1 expandir

    def setup_csv(self):
        """Abre o arquivo CSV e escreve o cabeçalho."""
        try:
            filename = f"acc_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            self.csv_file = open(filename, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            
            self.csv_writer.writerow(["Timestamp", "PacketID", "G_Lateral", "G_Longitudinal", "G_Vertical"])
            print(f"Salvando log em: {filename}")
            
        except IOError as e:
            print(f"Erro ao criar arquivo CSV: {e}")
            self.status_var.set("Erro ao criar CSV!")

    def update_data(self):
        """A função principal que lê os dados e atualiza a tela."""
        try:
            if self.shm is None:
                try:
                    self.shm = mmap.mmap(0, ctypes.sizeof(SPageFilePhysics), "acpmf_physics", mmap.ACCESS_READ)
                except FileNotFoundError:
                    self.status_var.set("Aguardando ACC... (Verifique broadcasting.json)")
                    self.root.after(1000, self.update_data)
                    return
            
            self.shm.seek(0)
            buffer = self.shm.read(ctypes.sizeof(SPageFilePhysics))
            dados_fisica = SPageFilePhysics.from_buffer_copy(buffer)
            current_packet_id = dados_fisica.packetId
            if current_packet_id == 0 or current_packet_id == self.last_packet_id:
                if current_packet_id == 0:
                    self.status_var.set("Conectado. Aguardando na pista...")
                self.root.after(16, self.update_data) # ~60Hz
                return
            
            self.last_packet_id = current_packet_id
            self.status_var.set("Conectado! Lendo dados...")

            #Coleta dos Dados
            g_lat = dados_fisica.accG[0]
            g_lon = dados_fisica.accG[2]
            g_ver = dados_fisica.accG[1]

            self.g_lat_var.set(f"{g_lat: 8.3f} G")
            self.g_lon_var.set(f"{g_lon: 8.3f} G")
            self.g_ver_var.set(f"{g_ver: 8.3f} G")

            #Salva planilha
            if self.csv_writer:
                timestamp = datetime.now().isoformat()
                self.csv_writer.writerow([timestamp, current_packet_id, g_lat, g_lon, g_ver])

        except Exception as e:
            print(f"Erro no loop de atualização: {e}")
            if isinstance(e, FileNotFoundError):
                self.shm = None
                self.status_var.set("Jogo desconectado. Tentando reconectar...")
            time.sleep(1)

        self.root.after(16, self.update_data)

    def on_close(self):
        """Chamado quando o usuário fecha a janela."""
        print("Fechando... Salvando arquivo CSV.")

        if self.csv_file:
            self.csv_file.close()
            print("Arquivo CSV salvo com segurança.")
        if self.shm:
            self.shm.close()

        self.root.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = TelemetryApp(root)

        root.after(16, app.update_data)

        root.mainloop()
        
    except Exception as e:
        print(f"Ocorreu um erro fatal: {e}")
    finally:
        print("Programa encerrado.")
