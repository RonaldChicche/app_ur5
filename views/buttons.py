from tkinter import messagebox

import tkinter as tk
import json
import os


class VistaBotones(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        self.selected_row = None
        self.buttons_por_fila = []

        # Botón Home
        home_btn = tk.Button(self, text="🏠 Home", bg="#3498db", fg="white", font=("Arial", 18, "bold"),
                             width=10, height=2, command=self.volver_home)
        home_btn.pack(pady=(20, 10))

        # Rutas desde config
        config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        self.rutas = config.get("rutas")

        self.campos = {
            "01": "Zoom In Vertical",
            "02": "Paneo Horizontal Recto",
            "03": "Paneo Horizontal Circular",
            "04": "Paneo Film"
        }

        # Contenedor general para centrar vertical y horizontalmente
        contenedor = tk.Frame(self, bg="white")
        contenedor.pack(pady=10)

        for i, ruta in enumerate(self.rutas["rutinas"]):
            fila = tk.Frame(self, bg="white")
            fila.pack(pady=5)

            nombre_archivo = os.path.basename(ruta)

            partes = os.path.splitext(nombre_archivo)[0].split('_')
            print(partes)
            no_prog = partes[1]

            # Label 
            label = tk.Label(fila, text=self.campos[no_prog] + ":", font=("Arial", 12, "bold"), bg="white", anchor="e", width=25)
            label.grid(row=0, column=0, padx=(10, 20), sticky="e")  # Alineado a la izquierda

            btn1 = tk.Button(fila, text="Preparar Movimiento", width=20, height=2, font=("Arial", 12, "bold"),
                             command=lambda idx=i: self.config_set(idx))
            btn2 = tk.Button(fila, text="Ejecutar", width=20, height=2, font=("Arial", 12, "bold"),
                             state="disabled", command=lambda idx=i: self.config_go(idx))

            btn1.grid(row=0, column=1, padx=10)
            btn2.grid(row=0, column=2, padx=10)
            self.buttons_por_fila.append((btn1, btn2))

        # Activar solo el primer botón de cada fila
        self.resetear_botones()

        # Botones inferiores
        control_frame = tk.Frame(self, bg="white")
        control_frame.pack(pady=30)

        btn_cfg = dict(width=10, height=2, font=("Arial", 12, "bold"))
        tk.Button(control_frame, text="▶ Play", bg="#2ecc71", fg="white", **btn_cfg, command=self.ejecutar_play).pack(side="left", padx=10)
        tk.Button(control_frame, text="⏸ Pause", bg="#f1c40f", fg="black", **btn_cfg, command=self.ejecutar_pause).pack(side="left", padx=10)
        tk.Button(control_frame, text="⏹ Stop", bg="#e74c3c", fg="white", **btn_cfg, command=self.ejecutar_stop).pack(side="left", padx=10)
        
    def resetear_botones(self):
        for btn1, btn2 in self.buttons_por_fila:
            btn1.config(state="normal")
            btn2.config(state="disabled")

    def config_set(self, idx):
        key = f"sec_{idx + 1:02d}"
        print(f"En la ruta: {idx} --> {key}")
        for i, (btn1, btn2) in enumerate(self.buttons_por_fila):
            if i == idx:
                btn1.config(state="disabled")
                btn2.config(state="normal")
            else:
                btn1.config(state="disabled")
                btn2.config(state="disabled")

        script = self.rutas["rutinas"][key]["set"]
        print(f"Preparando: {script}")
        controller = self.get_controller()
        if controller:
            result = controller.send_script_file(script)
            print("Ejecutando:", result)

    def config_go(self, idx):
        key = f"sec_{idx + 1:02d}"
        script = self.rutas["rutinas"][key]["go"]
        print(f"Ejecutando: {script}")
        controller = self.get_controller()
        if controller:
            result = controller.send_script_file(script)
            print("Ejecutando:", result)
        self.resetear_botones()

    def volver_home(self):
        script = self.rutas["home"]
        controller = self.get_controller()
        if controller:
            result = controller.send_script_file(script)
            print("Ejecutando:", result)
        self.resetear_botones()
        print("Regresando a Home...")

    def get_controller(self):
        app = self.winfo_toplevel()
        if hasattr(app, "ur_controller") and app.ur_controller:
            return app.ur_controller
        else:
            messagebox.showwarning("Sin conexión", "El controlador del robot no está conectado.")
            return None

    def ejecutar_play(self):
        controller = self.get_controller()
        if controller:
            result = controller.play()
            print("▶ Play:", result)

    def ejecutar_pause(self):
        controller = self.get_controller()
        if controller:
            result = controller.pause()
            print("⏸ Pause:", result)

    def ejecutar_stop(self):
        controller = self.get_controller()
        if controller:
            result = controller.stop()
            print("⏹ Stop:", result)
    
