"""Point d'entrée de l'application Dorking."""

import os
import sys

# Ajout du répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import messagebox


def check_dependencies():
    missing = []
    packages = {
        "customtkinter": "customtkinter",
        "requests": "requests",
        "duckduckgo_search": "duckduckgo-search",
    }
    for module, pkg in packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pkg)
    return missing


def main():
    missing = check_dependencies()
    if missing:
        root = tk.Tk()
        root.withdraw()
        msg = (
            f"Dépendances manquantes : {', '.join(missing)}\n\n"
            f"Exécutez : pip install {' '.join(missing)}"
        )
        messagebox.showerror("Installation requise", msg)
        root.destroy()
        print(msg)
        sys.exit(1)

    from ui.app import DorkingApp
    app = DorkingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
