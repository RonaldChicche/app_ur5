import tkinter as tk
import json

class VistaConfiguracion(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Cargar configuración desde JSON
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        self.campos = {}
        for campo in config["campos"]:
            label = tk.Label(self, text=campo["label"], font=("Arial", 12))
            label.pack(pady=(10, 0))

            if campo["type"] == "entry":
                entry = tk.Entry(self, font=("Arial", 12))
                entry.pack(pady=5, fill="x", padx=20)
                self.campos[campo["label"]] = entry

            elif campo["type"] == "dropdown":
                var = tk.StringVar(self)
                var.set(campo["options"][0])
                dropdown = tk.OptionMenu(self, var, *campo["options"])
                dropdown.config(font=("Arial", 12))
                dropdown.pack(pady=5, fill="x", padx=20)
                self.campos[campo["label"]] = var
