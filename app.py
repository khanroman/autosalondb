#app
import tkinter as tk
from tkinter import ttk
from gui import GuiManager
from operations import (
    add_sale_window,
    add_buyout_window
)
from reports import generate_sales_report, generate_buyouts_report, generate_custom_report

class AutoSalonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автосалон — Управление БД")
        self.gui = GuiManager(root, self)

        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Добавить продажу", command=lambda: add_sale_window(self)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Добавить выкуп", command=lambda: add_buyout_window(self)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить данные", command=self.gui.refresh_all_tables).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Отчет по продажам", command=lambda: generate_sales_report(self)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Отчет по выкупам", command=lambda: generate_buyouts_report(self)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Настраиваемый отчет", command=lambda: generate_custom_report(self)).pack(side="left", padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoSalonApp(root)
    root.geometry("800x600")
    root.mainloop()