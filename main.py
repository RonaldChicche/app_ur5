import tkinter as tk
from views.vista1 import VistaConfiguracion
from views.vista2 import VistaBotones

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("App con Aside y Vistas")
        self.geometry("700x400")

        # Contenedor principal
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Aside
        aside = tk.Frame(container, width=160, bg="#2c3e50")
        aside.pack(side="left", fill="y")

        # Área de contenido
        self.content = tk.Frame(container, bg="white")
        self.content.pack(side="right", fill="both", expand=True)

        # Botones del aside
        btn1 = tk.Button(aside, text="Configuración", fg="white", bg="#34495e",
                         font=("Arial", 12), command=self.mostrar_vista1)
        btn1.pack(fill="x", pady=10, padx=10)

        btn2 = tk.Button(aside, text="Acciones", fg="white", bg="#34495e",
                         font=("Arial", 12), command=self.mostrar_vista2)
        btn2.pack(fill="x", pady=10, padx=10)

        #
