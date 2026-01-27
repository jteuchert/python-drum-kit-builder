# Main: main application entry point (MVC pattern)

import tkinter as tk
from model import AppState
from view import AppView
from controller import AppController

def main():
    root = tk.Tk()

    model = AppState(number=5)
    view = AppView(root)
    view.pack(padx=10, pady=10)

    controller = AppController(model, view)

    root.mainloop()

if __name__ == "__main__":
    main()
