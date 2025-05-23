from tkinter import messagebox

import tkinter as tk
import os
import json
import time
import platform
import threading
import subprocess


class VistaConfiguracion(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Cargar configuración desde JSON
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        self.labels = {}

        # Campos estáticos a mostrar
        campos = {
            "Sistema operativo": config.get("os", "Desconocido"),
            "Directorio base": config.get("base_dir", ""),
            "Directorio de scripts": config.get("scripts_dir", ""),
            "Directorio de assets": config.get("assets_dir", "")
        }

        # Mostrar etiquetas con los valores
        for nombre_campo, valor in campos.items():
            label = tk.Label(self, text=nombre_campo + ":", font=("Arial", 12, "bold"), bg="white")
            label.pack(anchor="w", padx=20, pady=(10, 0))

            value_label = tk.Label(self, text=valor, font=("Arial", 12), bg="white", fg="gray25", wraplength=640, justify="left")
            value_label.pack(anchor="w", padx=20, pady=(0, 10))

            self.labels[nombre_campo] = value_label

        # Entry
        tk.Label(self, text="IP_HOST:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20, pady=(10, 0))

        self.entry_ip = tk.Entry(self, font=("Arial", 12))
        self.entry_ip.insert(0, config.get("IP_HOST", ""))
        self.entry_ip.pack(pady=5, fill="x", padx=20)

        # Circle state -> green:pin ok , red:pin error, no color: before action
        self.canvas = tk.Canvas(self, width=20, height=20, bg="white", highlightthickness=0)
        self.circle = self.canvas.create_oval(2, 2, 18, 18, fill="gray")
        self.canvas.pack(anchor="w", padx=20)

        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10, anchor="w", padx=20)
        # Button PING
        ping_btn = tk.Button(btn_frame, text="Ping", command=self.ping_ip, bg="#3498db", fg="white", font=("Arial", 11))
        ping_btn.pack(side="left", padx=5)
        # Button Connect
        connect_btn = tk.Button(btn_frame, text="Connect", command=self.connect_to_ur, bg="#2ecc71", fg="white", font=("Arial", 11))
        connect_btn.pack(side="left", padx=5)
    
    def connect_to_ur(self):
        ip = self.entry_ip.get().strip()
        if not ip:
            tk.messagebox.showwarning("Error", "IP no válida.")
            return

        app = self.winfo_toplevel()
        self.mostrar_popup_conexion()
        self.actualizar_popup("⏳ Conectando a " + ip)

        def conectar():
            try:
                con = app.connect(ip)
                if con:
                    self.actualizar_popup("✅ Conexión exitosa")

                    # Guardar IP en config.json
                    config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../config.json")
                    if os.path.exists(config_path):
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    else:
                        config = {}

                    config["robot_ip"] = ip
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2)

                    time.sleep(1)
                    self.cerrar_popup()
                    tk.messagebox.showinfo("Conectado", f"Robot conectado exitosamente a {ip}")
                else:
                    self.actualizar_popup("❌ Error de conexión")
                    time.sleep(1.5)
                    self.cerrar_popup()
                    tk.messagebox.showerror("Error", f"No se pudo conectar al robot en {ip}.")
            except Exception as e:
                self.actualizar_popup("❌ Excepción")
                time.sleep(1)
                self.cerrar_popup()
                tk.messagebox.showerror("Error de conexión", str(e))

        threading.Thread(target=conectar, daemon=True).start()

    def ping_ip(self):
        # Reads content from entry 
        # Triees to ping to the ip in entry
        # its result defines color for Circle state
        #pass
        ip = self.entry_ip.get().strip()
        if not ip:
            messagebox.showwarning("IP vacía", "Por favor ingresa una dirección IP.")
            return

        param = "-n" if platform.system().lower() == "windows" else "-c"
        response = subprocess.call(["ping", param, "1", ip], stdout=subprocess.DEVNULL)

        if response == 0:
            self.canvas.itemconfig(self.circle, fill="green")
        else:
            self.canvas.itemconfig(self.circle, fill="red")
            
    def mostrar_popup_conexion(self):
        self.popup = tk.Toplevel(self)
        self.popup.title("Conectando al robot")
        self.popup.geometry("300x120")
        self.popup.transient(self)  # Mantener encima de la ventana principal
        self.popup.grab_set()       # Bloquea la ventana principal
        self.popup.resizable(False, False)

        self.popup_label = tk.Label(self.popup, text="⏳ Conectando...", font=("Arial", 11))
        self.popup_label.pack(pady=30)

        self.update_idletasks()

    def actualizar_popup(self, texto):
        if hasattr(self, 'popup_label'):
            self.popup_label.config(text=texto)
            self.popup.update_idletasks()

    def cerrar_popup(self):
        if hasattr(self, 'popup') and self.popup.winfo_exists():
            self.popup.destroy()
