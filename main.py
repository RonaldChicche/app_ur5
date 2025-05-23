from views.config import VistaConfiguracion
from views.buttons import VistaBotones
from collections import defaultdict
from model.ur_controller import URRobotController

import os
import json
import time
import platform
import threading
import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Hilo virtual
        self.stop_event = threading.Event()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.title("App con Aside y Vistas")
        self.geometry("900x600")
        
        self.ur_controller = None  

        # Contenedor vertical principal
        layout = tk.Frame(self)
        layout.pack(fill="both", expand=True)

        # Barra superior con 3 secciones
        self.status_frame = tk.Frame(layout, bg="#2c3e50")
        self.status_frame.pack(fill="x")

        self.estado_conexion = tk.Label(self.status_frame, text="🔌 Desconectado", bg="#2c3e50", fg="white", width=30, height=3, anchor="w", font=("Arial", 10))
        self.estado_robot = tk.Label(self.status_frame, text="⏳ Robot: ---", bg="#2c3e50", fg="white", width=30, height=3, anchor="center", font=("Arial", 10))
        self.estado_programa = tk.Label(self.status_frame, text="▶️ Programa: ---", bg="#2c3e50", fg="white", width=30, height=3, anchor="e", font=("Arial", 10))

        self.estado_conexion.pack(side="left", fill="y")
        self.estado_robot.pack(side="left", fill="y")
        self.estado_programa.pack(side="left", fill="y")
        
        # Contenedor principal
        container = tk.Frame(layout)
        container.pack(fill="both", expand=True)

        # Aside
        aside = tk.Frame(container, width=160, bg="#2c3e50")
        aside.pack(side="left", fill="y")

        # Estado
        # self.estado_label = tk.Label(aside, text="Estado: ---", bg="white", fg="white", font=("Arial", 10), wraplength=140)
        # self.estado_label.pack(pady=20)

        # Área de contenido
        self.content = tk.Frame(container, bg="white")
        self.content.pack(side="right", fill="both", expand=True)

        # Instancia de vistas
        self.vista_config = VistaConfiguracion(self.content)
        self.vista_cmd = VistaBotones(self.content)

        # Coloca las vistas en el mismo lugar pero ocúltalas
        for vista in (self.vista_config, self.vista_cmd):
            vista.place(relwidth=1, relheight=1)

        # Botones del aside
        btn1 = tk.Button(aside, text="Configuración", fg="white", bg="#34495e",
                         font=("Arial", 12), command=self.mostrar_vista1)
        btn1.pack(fill="x", pady=10, padx=10)

        btn2 = tk.Button(aside, text="Acciones", fg="white", bg="#34495e",
                         font=("Arial", 12), command=self.mostrar_vista2)
        btn2.pack(fill="x", pady=10, padx=10)

        # Mostrar vista inicial
        self.mostrar_vista1()

    def mostrar_vista1(self):
        self.vista_config.lift()

    def mostrar_vista2(self):
        self.vista_cmd.lift()
    
    def on_close(self):
        print("Cerrando aplicación...")
        self.stop_event.set()  # Detiene el bucle del hilo
        self.destroy()   

    # def actualizar_estado_gui(self, texto):
    #     self.estado_label.config(text=texto)

    def connect(self, ip):
        self.ur_controller = URRobotController(ip)
        intentos = 5
        for intento in range(1, intentos + 1):
            conectado = self.ur_controller.dashboard.is_connected()
            if conectado:
                print(f"[✓] Conexión exitosa en intento {intento}")
                # Lanza hilo de inicialización y monitoreo
                self.iniciar_robot()
                return True
            else:
                print(f"[{intento}/{intentos}] Fallo de conexión, reintentando...")
                #time.sleep(1)

        print(f"❌ No se pudo conectar al robot después de {intentos} intentos.")
        return False

    def iniciar_robot(self):
        if not self.ur_controller.dashboard.is_connected():
            return

        if not self.ur_controller.dashboard.is_robot_ready():
            self.ur_controller.dashboard.auto_initialize()

        # Inicia monitoreo continuo
        threading.Thread(target=self.monitor_estado_robot, daemon=True).start()

    def monitor_estado_robot(self):
        while not self.stop_event.is_set():
            try:
                modo = self.ur_controller.dashboard.robot_mode().strip().upper()
                estado = self.ur_controller.dashboard.program_state().strip().upper()
                safety = self.ur_controller.dashboard.safety_status().strip().upper()

                # Determinar colores y texto amigable
                color_conexion = "#2ecc71" if "RUNNING" in modo or "NORMAL" in modo else "#e74c3c"
                color_programa = "#2ecc71" if estado == "PLAYING" else "#f1c40f" if estado == "PAUSED" else "#e74c3c"
                color_safety = "#2ecc71" if "NORMAL" in safety else "#f39c12" if "REDUCED" in safety else "#e74c3c"

                texto_conexion = f"🔌 {modo.capitalize()}"
                texto_programa = f"▶️ {estado.capitalize()}"
                texto_robot = f"🛡️ {safety.capitalize()}"

                # Actualizar GUI desde hilo seguro con after()
                self.after(0, lambda: self.actualizar_estado_conexion(texto_conexion, color_conexion))
                self.after(0, lambda: self.actualizar_estado_programa(texto_programa, color_programa))
                self.after(0, lambda: self.actualizar_estado_robot(texto_robot, color_safety))

                if "NORMAL" not in safety:
                    self.after(0, lambda: self.mostrar_popup_safety(safety.capitalize()))

            except Exception as e:
                self.after(0, lambda: self.actualizar_estado_conexion("❌ Error", "#e74c3c"))
                self.after(0, lambda: self.actualizar_estado_programa("❌", "#e74c3c"))
                self.after(0, lambda: self.actualizar_estado_robot("❌", "#e74c3c"))

            time.sleep(1.0)

        print("Fin Monitoreo")
    
    def actualizar_estado_conexion(self, texto, color="#34495e"):
        self.estado_conexion.config(text=texto, bg=color)

    def actualizar_estado_robot(self, texto, color="#34495e"):
        self.estado_robot.config(text=texto, bg=color)

    def actualizar_estado_programa(self, texto, color="#34495e"):
        self.estado_programa.config(text=texto, bg=color)

    def mostrar_popup_safety(self, mensaje):
        # Evitar múltiples popups si ya existe uno
        if hasattr(self, 'popup_safety') and self.popup_safety.winfo_exists():
            return

        self.popup_safety = tk.Toplevel(self)
        self.popup_safety.title("⚠️ Estado de Seguridad")
        self.popup_safety.geometry("400x150")
        self.popup_safety.resizable(False, False)
        self.popup_safety.transient(self)
        self.popup_safety.grab_set()

        label = tk.Label(self.popup_safety, text=f"🛡️ Seguridad: {mensaje}", font=("Arial", 11))
        label.pack(pady=15)

        btn = tk.Button(self.popup_safety, text="🔓 Desbloquear", bg="#e67e22", fg="white", font=("Arial", 11, "bold"),
                        command=lambda: self.desbloquear_robot())
        btn.pack(pady=5)

        cerrar = tk.Button(self.popup_safety, text="Cerrar", command=self.popup_safety.destroy)
        cerrar.pack(pady=5)

    def desbloquear_robot(self):
        try:
            self.ur_controller.dashboard.unlock_protective_stop()
            self.popup_safety.destroy()
            self.actualizar_estado_robot("🛡️ Desbloqueado", "#2ecc71")
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo desbloquear:\n{e}")


def load_config():
    current_os = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")

    config_path = os.path.join(BASE_DIR, "config.json")

    # Leer archivo JSON
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Agregar campos que serán útiles
    config["base_dir"] = BASE_DIR
    config["scripts_dir"] = SCRIPTS_DIR
    config["assets_dir"] = ASSETS_DIR
    config["os"] = current_os

    # Leer scripts:
    rutas = {"home": None, "rutinas": defaultdict(dict)}
    for archivo in os.listdir(SCRIPTS_DIR):
        if not archivo.endswith(".script"):
            continue
        
        ruta_completa = os.path.join(SCRIPTS_DIR, archivo)
        nombre_sin_ext = os.path.splitext(archivo)[0]
        
        if nombre_sin_ext.startswith("home"):
            rutas["home"] = ruta_completa

        elif nombre_sin_ext.startswith("sec_"):
            partes = nombre_sin_ext.split("_")
            if len(partes) >= 3:
                seccion = f"{partes[0]}_{partes[1]}"
                accion = partes[2]
                rutas["rutinas"][seccion][accion] = ruta_completa

    config["rutas"] = dict(rutas)

    # Guardar el archivo actualizado
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    # Guardar
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


if __name__ == '__main__':
    load_config()
    app = App()
    app.mainloop()
