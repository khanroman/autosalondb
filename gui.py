#gui
import tkinter as tk
from tkinter import ttk, Toplevel
from database import get_table_columns, fetch_all, load_table_data


class GuiManager:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Хранит состояние сортировки: {столбец: 'asc'/'desc'}
        self.sort_states = {}

        self.create_tab("Автомобили")
        self.create_tab("Клиенты")
        self.create_tab("Продажи")
        self.create_tab("Выкуп")

    def create_tab(self, table_name):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=table_name)

        tree = ttk.Treeview(frame, show="headings")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        columns = get_table_columns(table_name)
        display_columns = [col for col in columns if not col.startswith("ID_")]
        tree["columns"] = display_columns

        for col in display_columns:
            tree.heading(col, text=col, command=lambda c=col: self.sort_column(tree, table_name, c))
            tree.column(col, width=120 if col in ["ФИО", "VIN"] else 100)

        setattr(self.app, f"tree_{table_name}", tree)
        self.load_table(tree, table_name)

    def refresh_all_tables(self):
        for table in ["Автомобили", "Клиенты", "Продажи", "Выкуп"]:
            tree = getattr(self.app, f"tree_{table}", None)
            if tree:
                self.load_table(tree, table)

    def sort_column(self, tree, table_name, column):
        current_state = self.sort_states.get(column, None)

        if current_state == "asc":
            direction = "desc"
            arrow = " ↓"
        else:
            direction = "asc"
            arrow = " ↑"

        # Убираем все стрелочки
        for col in tree["columns"]:
            tree.heading(col, text=col.split(" ")[0])

        # Добавляем новую
        tree.heading(column, text=f"{column}{arrow}")

        # Обновляем состояние
        self.sort_states.clear()
        self.sort_states[column] = direction

        # Перезагружаем таблицу с сортировкой
        self.load_table(tree, table_name, sort_by=column, sort_order=direction)

    def load_table(self, tree, table_name, sort_by=None, sort_order="asc"):
        # Очистка таблицы
        for row in tree.get_children():
            tree.delete(row)

        all_columns = get_table_columns(table_name)
        display_columns = [col for col in all_columns if not col.startswith("ID_")]

        if table_name == "Автомобили":
            query = """
                SELECT 
                    VIN,
                    Марка,
                    Модель,
                    Пробег,
                    Год_выпуска,
                    Цена,
                    Состояние,
                    Статус_склада
                FROM Автомобили
            """

            order_col_map = {
                "VIN": "VIN",
                "Марка": "Марка",
                "Модель": "Модель",
                "Пробег": "CAST(Пробег AS INTEGER)",
                "Год_выпуска": "CAST(Год_выпуска AS INTEGER)",
                "Цена": "CAST(Цена AS REAL)",
                "Состояние": "Состояние",
                "Статус_склада": "Статус_склада"
            }

            if sort_by and sort_by in order_col_map:
                query += f" ORDER BY {order_col_map[sort_by]} {sort_order.upper()}"

            rows = fetch_all(query)

            columns = ["VIN", "Марка", "Модель", "Пробег", "Год_выпуска", "Цена", "Состояние", "Статус_склада"]
            tree["columns"] = columns

            for col in columns:
                tree.heading(col, text=col, command=lambda c=col: self.sort_column(tree, table_name, c))
                tree.column(col, width=120 if col in ["VIN"] else 100)

            for row in rows:
                display_row = [
                    row[0],  # VIN
                    row[1],  # Марка
                    row[2],  # Модель
                    row[3],  # Пробег
                    row[4],  # Год выпуска
                    f"{row[5]:.2f}" if row[5] is not None else "",  # Цена
                    row[6],  # Состояние
                    row[7],  # Статус склада
                ]
                tree.insert("", "end", values=display_row)

        elif table_name == "Клиенты":
            query = """
                SELECT 
                    ФИО,
                    Телефон,
                    Адрес
                FROM Клиенты
            """

            order_col_map = {
                "ФИО": "ФИО",
                "Телефон": "Телефон",
                "Адрес": "Адрес"
            }

            if sort_by and sort_by in order_col_map:
                query += f" ORDER BY {order_col_map[sort_by]} {sort_order.upper()}"

            rows = fetch_all(query)

            columns = ["ФИО", "Телефон", "Адрес"]
            tree["columns"] = columns

            for col in columns:
                tree.heading(col, text=col, command=lambda c=col: self.sort_column(tree, table_name, c))
                tree.column(col, width=120 if col == "ФИО" else 100)

            for row in rows:
                display_row = [
                    row[0],  # ФИО
                    row[1],  # Телефон
                    row[2],  # Адрес
                ]
                tree.insert("", "end", values=display_row)

        elif table_name == "Продажи":
            query = """
                SELECT 
                    Продажи.ID_Продажи,
                    Автомобили.VIN,
                    Клиенты.ФИО,
                    Продажи.Дата_Продажи,
                    Продажи.Сумма,
                    Выкуп.Сумма_Выкупа,
                    (Продажи.Сумма - IFNULL(Выкуп.Сумма_Выкупа, 0)) AS Прибыль,
                    Продавец
                FROM Продажи
                JOIN Автомобили ON Продажи.ID_Автомобиля = Автомобили.ID_Автомобиля
                JOIN Клиенты ON Продажи.ID_Клиента = Клиенты.ID_Клиента
                LEFT JOIN Выкуп ON Автомобили.ID_Автомобиля = Выкуп.ID_Автомобиля
            """

            order_col_map = {
                "VIN": "Автомобили.VIN",
                "ФИО": "Клиенты.ФИО",
                "Дата продажи": "Продажи.Дата_Продажи",
                "Сумма": "CAST(Продажи.Сумма AS REAL)",
                "Сумма выкупа": "CAST(IFNULL(Выкуп.Сумма_Выкупа, 0) AS REAL)",
                "Прибыль": "CAST((Продажи.Сумма - IFNULL(Выкуп.Сумма_Выкупа, 0)) AS REAL)",
                "Продавец": "Продавец"
            }

            if sort_by and sort_by in order_col_map:
                query += f" ORDER BY {order_col_map[sort_by]} {sort_order.upper()}"

            rows = fetch_all(query)

            columns = ["VIN", "ФИО", "Дата продажи", "Сумма", "Сумма выкупа", "Прибыль", "Продавец"]
            tree["columns"] = columns

            for col in columns:
                tree.heading(col, text=col, command=lambda c=col: self.sort_column(tree, table_name, c))
                tree.column(col, width=120 if col in ["ФИО", "VIN"] else 100)

            for row in rows:
                display_row = [
                    row[1],  # VIN
                    row[2],  # ФИО
                    row[3],  # Дата продажи
                    f"{row[4]:.2f}" if row[4] is not None else "",  # Сумма
                    f"{row[5]:.2f}" if row[5] is not None else "0.00",  # Сумма выкупа
                    f"{row[6]:.2f}" if row[6] is not None else "0.00",  # Прибыль
                    row[7],  # Продавец
                ]
                tree.insert("", "end", values=display_row)

        elif table_name == "Выкуп":
            query = """
                SELECT 
                    Выкуп.Дата_Выкупа,
                    Выкуп.Сумма_Выкупа,
                    Выкуп.Выкупщик,
                    Автомобили.VIN,
                    Клиенты.ФИО
                FROM Выкуп
                JOIN Автомобили ON Выкуп.ID_Автомобиля = Автомобили.ID_Автомобиля
                JOIN Клиенты ON Выкуп.ID_Клиента = Клиенты.ID_Клиента
            """

            order_col_map = {
                "Дата выкупа": "Выкуп.Дата_Выкупа",
                "Сумма выкупа": "CAST(Выкуп.Сумма_Выкупа AS REAL)",
                "Выкупщик": "Выкуп.Выкупщик",
                "VIN": "Автомобили.VIN",
                "ФИО": "Клиенты.ФИО"
            }

            if sort_by and sort_by in order_col_map:
                query += f" ORDER BY {order_col_map[sort_by]} {sort_order.upper()}"

            rows = fetch_all(query)

            columns = ["Дата выкупа", "Сумма выкупа", "Выкупщик", "VIN", "ФИО"]
            tree["columns"] = columns

            for col in columns:
                tree.heading(col, text=col, command=lambda c=col: self.sort_column(tree, table_name, c))
                tree.column(col, width=120 if col in ["Дата выкупа", "VIN", "ФИО"] else 100)

            for row in rows:
                display_row = [
                    row[0],  # Дата выкупа
                    f"{row[1]:.2f}" if row[1] is not None else "0.00",  # Сумма выкупа
                    row[2],  # Выкупщик
                    row[3],  # VIN
                    row[4],  # ФИО клиента
                ]
                tree.insert("", "end", values=display_row)