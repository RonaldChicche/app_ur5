import tkinter as tk

class VistaBotones(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        botones = [
            {"texto": "Inicio", "accion": lambda: print("Inicio presionado")},
            {"texto": "Guardar", "accion": lambda: print("Guardar presionado")},
            {"texto": "Eliminar", "accion": lambda: print("Eliminar presionado")},
            {"texto": "Actualizar", "accion": lambda: print("Actualizar presionado")},
        ]

        for boton in botones:
            btn = tk.Button(self, text=boton["texto"], font=("Arial", 14), width=20,
                            height=2, bg="#3498db", fg="white", command=boton["accion"])
            btn.pack(pady=10)
