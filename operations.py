#operations
import tkinter as tk
from tkinter import ttk, Toplevel, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from database import execute_query, fetch_one, fetch_all
from config import SELLERS, BUYERS

def add_sale_window(app):
    window = Toplevel(app.root)
    window.title("Добавить продажу")
    window.geometry("400x350")

    fields = {
        "VIN": "VIN автомобиля (17 символов)",
        "ФИО": "ФИО клиента",
        "Телефон": "Номер телефона (11 цифр)",
        "Адрес": "Адрес клиента",
        "Дата_Продажи": "Дата продажи (YYYY-MM-DD)",
        "Сумма": "Сумма продажи",
        "Продавец": "Продавец"
    }

    entries = {}

    for key, label in fields.items():
        row = ttk.Frame(window)
        row.pack(fill="x", pady=5)

        ttk.Label(row, text=label, width=25).pack(side="left")

        if key == "Дата_Продажи":
            date_entry = DateEntry(row, date_pattern='yyyy-mm-dd')
            date_entry.pack(side="right", fill="x", expand=True, padx=5)
            entries[key] = date_entry
        elif key == "Продавец":
            combo = ttk.Combobox(row, values=SELLERS)
            combo.pack(side="right", fill="x", expand=True, padx=5)
            entries[key] = combo
        else:
            entry = ttk.Entry(row)
            entry.pack(side="right", fill="x", expand=True, padx=5)
            entries[key] = entry

    ttk.Button(
        window,
        text="Добавить",
        command=lambda: save_sale(entries, window, app)
    ).pack(pady=10)

def save_sale(entries, window, app):
    vin = entries["VIN"].get().strip()
    client_data = {
        "ФИО": entries["ФИО"].get(),
        "Телефон": entries["Телефон"].get(),
        "Адрес": entries["Адрес"].get()
    }
    sale_data = {
        "Дата_Продажи": entries["Дата_Продажи"].get(),
        "Сумма": entries["Сумма"].get(),
        "Продавец": entries["Продавец"].get()
    }

    if len(vin) != 17:
        messagebox.showerror("Ошибка", "VIN должен содержать 17 символов.")
        return
    if not client_data["Телефон"].isdigit() or len(client_data["Телефон"]) != 11:
        messagebox.showerror("Ошибка", "Телефон должен состоять из 11 цифр.")
        return

    try:
        car_id_row = fetch_one("SELECT ID_Автомобиля FROM Автомобили WHERE VIN=?", (vin,))
        if not car_id_row:
            messagebox.showerror("Ошибка", "Автомобиль с таким VIN не найден.")
            return
        car_id = car_id_row[0]

        query_client = "INSERT INTO Клиенты (ФИО, Телефон, Адрес) VALUES (?, ?, ?)"
        execute_query(query_client, (client_data["ФИО"], client_data["Телефон"], client_data["Адрес"]))
        client_id = fetch_one("SELECT last_insert_rowid()")[0]

        query_sale = """
            INSERT INTO Продажи (ID_Автомобиля, ID_Клиента, Дата_Продажи, Сумма, Продавец)
            VALUES (?, ?, ?, ?, ?)
        """
        execute_query(query_sale, (
            car_id,
            client_id,
            sale_data["Дата_Продажи"],
            float(sale_data["Сумма"]),
            sale_data["Продавец"]
        ))

        execute_query("UPDATE Автомобили SET Статус_склада = 'Продан' WHERE ID_Автомобиля = ?", (car_id,))

        app.gui.refresh_all_tables()
        messagebox.showinfo("Успех", "Продажа успешно добавлена!")
        window.destroy()

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def add_buyout_window(app):
    window = Toplevel(app.root)
    window.title("Добавить выкуп")
    window.geometry("400x600")

    fields = {
        "VIN": "VIN автомобиля (17 символов)",
        "Марка": "Марка автомобиля",
        "Модель": "Модель автомобиля",
        "Пробег": "Пробег в км (до 999 999)",
        "Год_выпуска": "Год выпуска (1900 - текущий год)",
        "Цена_для_публикации": "Цена для публикации",
        "Состояние": "Состояние авто",
        "Дата_Выкупа": "Дата выкупа",
        "Сумма_Выкупа": "Сумма выкупа",
        "Выкупщик": "Выкупщик",
        "ФИО": "ФИО клиента",
        "Телефон": "Номер телефона (11 цифр)",
        "Адрес": "Адрес клиента"
    }

    entries = {}

    for key, label in fields.items():
        row = ttk.Frame(window)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text=label, width=25).pack(side="left")

        if key == "Состояние":
            combo = ttk.Combobox(row, values=["(A) Отличное", "(B) Хорошее", "(C) Среднее", "(D) Плохое"])
            combo.pack(side="right", fill="x", expand=True, padx=5)
            entries[key] = combo
        elif key == "Дата_Выкупа":
            date_entry = DateEntry(row, date_pattern='yyyy-mm-dd')
            date_entry.pack(side="right", fill="x", expand=True, padx=5)
            entries[key] = date_entry
        elif key == "Выкупщик":
            combo = ttk.Combobox(row, values=BUYERS)
            combo.pack(side="right", fill="x", expand=True, padx=5)
            entries[key] = combo
        else:
            entry = ttk.Entry(row)
            entry.pack(side="right", fill="x", expand=True, padx=5)
            entries[key] = entry

    ttk.Button(
        window,
        text="Добавить",
        command=lambda: save_buyout(entries, window, app)
    ).pack(pady=10)

def save_buyout(entries, window, app):
    vin = entries["VIN"].get().strip()
    car_data = {
        "Марка": entries["Марка"].get(),
        "Модель": entries["Модель"].get(),
        "Пробег": entries["Пробег"].get(),
        "Год_выпуска": entries["Год_выпуска"].get(),
        "Цена_для_публикации": entries["Цена_для_публикации"].get(),
        "Состояние": entries["Состояние"].get()[1]
    }
    client_data = {
        "ФИО": entries["ФИО"].get(),
        "Телефон": entries["Телефон"].get(),
        "Адрес": entries["Адрес"].get()
    }
    buyout_data = {
        "Дата_Выкупа": entries["Дата_Выкупа"].get(),
        "Сумма_Выкупа": entries["Сумма_Выкупа"].get(),
        "Выкупщик": entries["Выкупщик"].get()
    }

    if len(vin) != 17:
        messagebox.showerror("Ошибка", "VIN должен содержать 17 символов.")
        return
    if not car_data["Пробег"].isdigit() or not 0 <= int(car_data["Пробег"]) <= 999999:
        messagebox.showerror("Ошибка", "Пробег должен быть числом от 0 до 999 999.")
        return

    year = car_data["Год_выпуска"]
    current_year = datetime.now().year
    if not year.isdigit() or not 1900 <= int(year) <= current_year:
        messagebox.showerror("Ошибка", f"Год выпуска должен быть от 1900 до {current_year}.")
        return

    try:
        price_pub = float(car_data["Цена_для_публикации"])
        buyout_sum = float(buyout_data["Сумма_Выкупа"])
        if price_pub < buyout_sum:
            messagebox.showerror("Ошибка", "Цена должна быть не меньше суммы выкупа.")
            return
    except ValueError:
        messagebox.showerror("Ошибка", "Цена или сумма указаны неверно.")
        return

    if not client_data["Телефон"].isdigit() or len(client_data["Телефон"]) != 11:
        messagebox.showerror("Ошибка", "Телефон должен состоять из 11 цифр.")
        return

    try:
        query_car = """
            INSERT INTO Автомобили (VIN, Марка, Модель, Пробег, Год_выпуска, Цена, Состояние, Статус_склада)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(query_car, (
            vin,
            car_data["Марка"],
            car_data["Модель"],
            int(car_data["Пробег"]),
            int(car_data["Год_выпуска"]),
            float(car_data["Цена_для_публикации"]),
            car_data["Состояние"],
            "На складе"
        ))
        car_id = fetch_one("SELECT last_insert_rowid()")[0]

        query_client = "INSERT INTO Клиенты (ФИО, Телефон, Адрес) VALUES (?, ?, ?)"
        execute_query(query_client, (
            client_data["ФИО"],
            client_data["Телефон"],
            client_data["Адрес"]
        ))
        client_id = fetch_one("SELECT last_insert_rowid()")[0]

        query_buyout = """
            INSERT INTO Выкуп (ID_Автомобиля, ID_Клиента, Дата_Выкупа, Сумма_Выкупа, Выкупщик)
            VALUES (?, ?, ?, ?, ?)
        """
        execute_query(query_buyout, (
            car_id,
            client_id,
            buyout_data["Дата_Выкупа"],
            float(buyout_data["Сумма_Выкупа"]),
            buyout_data["Выкупщик"]
        ))

        app.gui.refresh_all_tables()
        messagebox.showinfo("Успех", "Выкуп успешно добавлен!")
        window.destroy()

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))