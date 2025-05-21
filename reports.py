#reports
import tkinter as tk
from tkinter import ttk, Toplevel, messagebox
from database import fetch_all
from config import BUYERS
from tkcalendar import DateEntry


def generate_sales_report(app):
    def show_report(start_cal, end_cal, buyer_combo, seller_combo):
        start_date = start_cal.get()
        end_date = end_cal.get()
        selected_buyer = buyer_combo.get() if buyer_combo else None
        selected_seller = seller_combo.get() if seller_combo else None

        query = """
            SELECT 
                Автомобили.VIN,
                Продажи.Дата_Продажи,
                Клиенты.ФИО,
                Выкуп.Выкупщик,
                Продавец,
                (Продажи.Сумма - IFNULL(Выкуп.Сумма_Выкупа, 0)) AS Прибыль
            FROM Продажи
            JOIN Автомобили ON Продажи.ID_Автомобиля = Автомобили.ID_Автомобиля
            JOIN Клиенты ON Продажи.ID_Клиента = Клиенты.ID_Клиента
            LEFT JOIN Выкуп ON Автомобили.ID_Автомобиля = Выкуп.ID_Автомобиля
            WHERE Продажи.Дата_Продажи BETWEEN ? AND ?
        """

        params = [start_date, end_date]

        if selected_seller:
            query += " AND Продавец = ?"
            params.append(selected_seller)
        if selected_buyer:
            query += " AND Выкуп.Выкупщик = ?"
            params.append(selected_buyer)

        rows = fetch_all(query, params)

        # Создаем окно отчета
        report_window = Toplevel(app.root)
        report_window.title("Отчет по продажам")
        report_window.geometry("800x600")

        tree = ttk.Treeview(report_window, columns=[
            "VIN", "Дата продажи", "ФИО клиента", "Выкупщик", "Продавец", "Прибыль"
        ], show="headings")

        for col in tree["columns"]:
            tree.heading(col, text=col, command=lambda c=col: sort_column(tree, rows, c, tree["columns"]))
            tree.column(col, width=120)

        tree.pack(fill="both", expand=True)

        total_profit = 0
        for row in rows:
            profit = float(row[5]) if row[5] else 0
            total_profit += profit
            tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], f"{profit:.2f}"))

        footer = ttk.Frame(report_window)
        footer.pack(pady=10)
        ttk.Label(footer, text=f"Общая прибыль: {total_profit:.2f}", font=("Arial", 12, "bold")).pack()

    open_report_window("Отчет по продажам", show_report, with_seller=True, with_buyer=True)


def generate_buyouts_report(app):
    def show_report(start_cal, end_cal, buyer_combo, seller_combo):
        start_date = start_cal.get()
        end_date = end_cal.get()
        selected_buyer = buyer_combo.get() if buyer_combo else None

        query = """
            SELECT 
                Автомобили.VIN,
                Выкуп.Дата_Выкупа,
                Клиенты.ФИО,
                Выкуп.Выкупщик,
                Выкуп.Сумма_Выкупа
            FROM Выкуп
            JOIN Автомобили ON Выкуп.ID_Автомобиля = Автомобили.ID_Автомобиля
            JOIN Клиенты ON Выкуп.ID_Клиента = Клиенты.ID_Клиента
            WHERE Выкуп.Дата_Выкупа BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        if selected_buyer:
            query += " AND Выкуп.Выкупщик = ?"
            params.append(selected_buyer)

        rows = fetch_all(query, params)

        report_window = Toplevel(app.root)
        report_window.title("Отчет по выкупам")
        report_window.geometry("700x500")

        tree = ttk.Treeview(report_window, columns=[
            "VIN", "Дата выкупа", "ФИО клиента", "Выкупщик", "Сумма выкупа"
        ], show="headings")

        for col in tree["columns"]:
            tree.heading(col, text=col, command=lambda c=col: sort_column(tree, rows, c, tree["columns"]))
            tree.column(col, width=140)

        tree.pack(fill="both", expand=True)

        total_sum = 0
        for row in rows:
            amount = float(row[4]) if row[4] else 0
            total_sum += amount
            tree.insert("", "end", values=(row[0], row[1], row[2], row[3], f"{amount:.2f}"))

        footer = ttk.Frame(report_window)
        footer.pack(pady=10)
        ttk.Label(footer, text=f"Общая сумма выкупов: {total_sum:.2f}", font=("Arial", 12, "bold")).pack()

    open_report_window("Отчет по выкупам", show_report, with_seller=False, with_buyer=True)


def generate_custom_report(app):
    CUSTOM_REPORT_COLUMNS = {
        "VIN": "Автомобили.VIN",
        "Марка": "Автомобили.Марка",
        "Модель": "Автомобили.Модель",
        "Пробег": "Автомобили.Пробег",
        "Год выпуска": "Автомобили.Год_выпуска",
        "Цена": "Автомобили.Цена",
        "Состояние": "Автомобили.Состояние",
        "Статус склада": "Автомобили.Статус_склада",
        "Выкупщик": "Выкуп.Выкупщик",
        "Сумма выкупа": "Выкуп.Сумма_Выкупа",
        "ФИО клиента-продавца": "Клиенты.ФИО",
        "Телефон клиента-продавца": "Клиенты.Телефон",
        "Адрес клиента-продавца": "Клиенты.Адрес",
        "ФИО клиента-покупателя": """
            (SELECT КлиентыПокупатель.ФИО FROM Продажи
             JOIN Клиенты AS КлиентыПокупатель ON Продажи.ID_Клиента = КлиентыПокупатель.ID_Клиента
             WHERE Продажи.ID_Автомобиля = Автомобили.ID_Автомобиля)
        """,
        "Телефон клиента-покупателя": """
            (SELECT КлиентыПокупатель.Телефон FROM Продажи
             JOIN Клиенты AS КлиентыПокупатель ON Продажи.ID_Клиента = КлиентыПокупатель.ID_Клиента
             WHERE Продажи.ID_Автомобиля = Автомобили.ID_Автомобиля)
        """,
        "Адрес клиента-покупателя": """
            (SELECT КлиентыПокупатель.Адрес FROM Продажи
             JOIN Клиенты AS КлиентыПокупатель ON Продажи.ID_Клиента = КлиентыПокупатель.ID_Клиента
             WHERE Продажи.ID_Автомобиля = Автомобили.ID_Автомобиля)
        """
    }

    def show_report(start_date, end_date, column_vars):
        nonlocal app
        selected_columns = [col for col, var in column_vars.items() if var.get()]
        if not selected_columns:
            messagebox.showwarning("Ошибка", "Выберите хотя бы один столбец для отчета.")
            return

        columns_sql = ", ".join([CUSTOM_REPORT_COLUMNS[col] for col in selected_columns])

        query = f"""
            SELECT {columns_sql}
            FROM Автомобили
            LEFT JOIN Выкуп ON Автомобили.ID_Автомобиля = Выкуп.ID_Автомобиля
            LEFT JOIN Клиенты ON Выкуп.ID_Клиента = Клиенты.ID_Клиента
            WHERE Выкуп.Дата_Выкупа BETWEEN ? AND ?
        """

        rows = fetch_all(query, [start_date, end_date])

        report_window = Toplevel(app.root)
        report_window.title("Настраиваемый отчет")
        report_window.geometry("1000x600")

        tree = ttk.Treeview(report_window, columns=selected_columns, show="headings")
        for col in selected_columns:
            tree.heading(col, text=col, command=lambda c=col: sort_column(tree, rows, c, selected_columns))
            tree.column(col, width=120)
        tree.pack(fill="both", expand=True)

        for row in rows:
            tree.insert("", "end", values=row)

    def open_column_selection(start_cal, end_cal):
        start_date = start_cal.get()
        end_date = end_cal.get()

        window = Toplevel()
        window.title("Выбор столбцов")
        window.geometry("400x400")

        frame = ttk.Frame(window)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        canvas = tk.Canvas(frame)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        column_vars = {}
        for col in CUSTOM_REPORT_COLUMNS.keys():
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(scrollable_frame, text=col, variable=var).pack(anchor="w")
            column_vars[col] = var

        def on_submit():
            window.destroy()
            show_report(start_date, end_date, column_vars)

        ttk.Button(window, text="Сформировать", command=on_submit).pack(pady=10)

    # Окно с выбором дат
    window = Toplevel()
    window.title("Настраиваемый отчет")
    window.geometry("400x300")

    frame = ttk.Frame(window)
    frame.pack(padx=10, pady=10)

    start_cal = DateEntry(frame, date_pattern='yyyy-mm-dd')
    end_cal = DateEntry(frame, date_pattern='yyyy-mm-dd')

    ttk.Label(frame, text="Начальная дата").grid(row=0, column=0, sticky="w")
    start_cal.grid(row=0, column=1, sticky="ew")

    ttk.Label(frame, text="Конечная дата").grid(row=1, column=0, sticky="w")
    end_cal.grid(row=1, column=1, sticky="ew")

    ttk.Button(frame, text="Далее", command=lambda: (
        open_column_selection(start_cal, end_cal),
        window.destroy()
    )).grid(row=5, column=0, columnspan=2, pady=10)

    frame.grid_columnconfigure(1, weight=1)


def open_report_window(title, callback, with_seller=False, with_buyer=False):
    window = Toplevel()
    window.title(title)
    window.geometry("400x300")

    frame = ttk.Frame(window)
    frame.pack(padx=10, pady=10)

    ttk.Label(frame, text="Начальная дата").grid(row=0, column=0, sticky="w")
    start_cal = DateEntry(frame, date_pattern='yyyy-mm-dd')
    start_cal.grid(row=0, column=1, sticky="ew")

    ttk.Label(frame, text="Конечная дата").grid(row=1, column=0, sticky="w")
    end_cal = DateEntry(frame, date_pattern='yyyy-mm-dd')
    end_cal.grid(row=1, column=1, sticky="ew")

    buyer_combo = None
    seller_combo = None

    if with_buyer:
        ttk.Label(frame, text="Выкупщик").grid(row=2, column=0, sticky="w")
        buyer_combo = ttk.Combobox(frame, values=BUYERS)
        buyer_combo.grid(row=2, column=1, sticky="ew")

    if with_seller:
        ttk.Label(frame, text="Продавец").grid(row=3, column=0, sticky="w")
        seller_combo = ttk.Combobox(frame, values=["Заргарян А.", "Язовских С.", "Кириллов А.", "Туник Д."])
        seller_combo.grid(row=3, column=1, sticky="ew")

    def handle_callback():
        callback(start_cal, end_cal, buyer_combo, seller_combo)

    ttk.Button(frame, text="Сформировать", command=handle_callback).grid(
        row=5, column=0, columnspan=2, pady=10
    )

    frame.grid_columnconfigure(1, weight=1)


# --- Вспомогательная функция сортировки ---
sort_state = {}  # Хранит состояние сортировки: {"column": "asc" или "desc"}

def sort_column(tree, full_data, column_name, all_columns):
    global sort_state

    # Убираем стрелки у всех заголовков
    for col in tree["columns"]:
        tree.heading(col, text=col.split(" ")[0])

    # Переключаем направление сортировки
    current_state = sort_state.get(column_name, None)
    if current_state == "asc":
        direction = "desc"
        arrow = " ↓"
    else:
        direction = "asc"
        arrow = " ↑"

    sort_state[column_name] = direction

    # Меняем текст заголовка
    tree.heading(column_name, text=f"{column_name}{arrow}")

    # Сортируем данные
    idx = list(all_columns).index(column_name)
    try:
        sorted_data = sorted(full_data, key=lambda x: x[idx] if x[idx] is not None else '', reverse=(direction == "desc"))
    except IndexError:
        return

    # Очищаем дерево
    for row in tree.get_children():
        tree.delete(row)

    # Вставляем отсортированные данные
    for row in sorted_data:
        tree.insert("", "end", values=row)