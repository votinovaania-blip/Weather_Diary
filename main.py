import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x500")

        self.records = []
        self.load_from_file()

        # Поля ввода
        input_frame = tk.LabelFrame(root, text="Новая запись", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="e")
        self.date_entry = tk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="e")
        self.temp_entry = tk.Entry(input_frame, width=8)
        self.temp_entry.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Описание погоды:").grid(row=1, column=0, sticky="e")
        self.desc_entry = tk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(row=1, column=4, padx=10)

        tk.Button(input_frame, text="Добавить запись", command=self.add_record, bg="lightgreen").grid(row=2, column=0, columnspan=5, pady=5)

        # Фильтры
        filter_frame = tk.LabelFrame(root, text="Фильтры", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0)
        self.filter_date_entry = tk.Entry(filter_frame, width=12)
        self.filter_date_entry.grid(row=0, column=1)

        tk.Label(filter_frame, text="Температура >").grid(row=0, column=2)
        self.filter_temp_entry = tk.Entry(filter_frame, width=5)
        self.filter_temp_entry.grid(row=0, column=3)

        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=4, padx=10)
        tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=5)

        # Таблица записей
        self.tree = ttk.Treeview(root, columns=("date", "temp", "description", "precip"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precip", text="Осадки")
        self.tree.column("date", width=100)
        self.tree.column("temp", width=80)
        self.tree.column("description", width=300)
        self.tree.column("precip", width=80)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопки сохранения/загрузки
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(btn_frame, text="Сохранить в JSON", command=self.save_to_file, bg="lightblue").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Загрузить из JSON", command=self.load_from_file).pack(side="left", padx=5)

        self.update_table()

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_record(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        try:
            temp_val = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        self.records.append({
            "date": date,
            "temperature": temp_val,
            "description": desc,
            "precipitation": precip
        })
        self.update_table()
        self.clear_inputs()

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

    def update_table(self, filtered_records=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = filtered_records if filtered_records is not None else self.records
        for rec in data:
            precip_str = "Да" if rec["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(
                rec["date"],
                rec["temperature"],
                rec["description"],
                precip_str
            ))

    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        filtered = self.records[:]

        if filter_date:
            filtered = [r for r in filtered if r["date"] == filter_date]

        if filter_temp_str:
            try:
                temp_threshold = float(filter_temp_str)
                filtered = [r for r in filtered if r["temperature"] > temp_threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура в фильтре должна быть числом")
                return

        self.update_table(filtered)

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()

    def save_to_file(self):
        with open("weather_data.json", "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Сохранено", "Записи сохранены в weather_data.json")

    def load_from_file(self):
        if not os.path.exists("weather_data.json"):
            return
        try:
            with open("weather_data.json", "r", encoding="utf-8") as f:
                self.records = json.load(f)
            self.update_table()
            messagebox.showinfo("Загружено", "Данные загружены из weather_data.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()