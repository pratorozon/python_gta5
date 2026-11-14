import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import math
import sys
import ctypes

# --- Настройки ---
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

DATA_FILE = os.path.join(SCRIPT_DIR, "skills_config.json")

# Данные по навыкам
SKILLS = {
    "Рыбак": {"reqs": [25, 75, 200, 400, 600, 1000], "desc": "Профессия. 3, 4, 5, 6 уровни открывают больше рыбы."},
    "Охотник": {"reqs": [100, 150, 200, 250, 300], "desc": "Профессия. Каждый уровень повышает мин. качество шкур.\nШанс сохранить прочность разделочного ножа."},
    "Кладоискатель": {"reqs": [100, 200, 300, 400, 500], "desc": "Профессия. Каждый уровень снижает шанс найти хлам.\n+10% к цене сдачи сокровищ за уровень."},
    "Фермер": {"reqs": [500, 500, 1000, 1000, 1500], "desc": "Профессия. Рост оплаты каждый уровень.\n2 ур. — трактор для прополки.\n3 ур. — посадка пшеницы и сбор на комбайне.\n5 ур. — самолёт для распыления химикатов."},
    "Строитель": {"reqs": [1500, 2250, 3000, 3750, 4500], "desc": "Профессия. Рост оплаты каждый уровень.\n3 ур. — работа на грузоподъёмнике."},
    "Шахтер": {"reqs": [1000, 1500, 2000, 2500, 3000], "desc": "Профессия. Рост оплаты каждый уровень.\n3 ур. — работа на бульдозере."},
    "Работник порта": {"reqs": [1500, 2250, 3000, 3750, 4500], "desc": "Профессия. Рост оплаты каждый уровень.\n3 ур. — работа на контейнерном погрузчике."},
    "Таксист": {"reqs": [100, 200, 300, 400, 500], "desc": "Профессия. Постепенный тюнинг авто каждый уровень.\n1 ур. — BF Olivia A7\n2 ур. — Benefactor Schafter\n3 ур. — Enus Deit\n4 ур. — Benefactor E-Series 63 W213\n5 ур. — Benefactor S-series W223, работа на личном авто."},
    "Водолаз": {"reqs": [85, 170, 255, 340, 425], "desc": "Профессия. Рост оплаты каждый уровень.\n3 ур. — работа в озере Сэнди-Шорс.\n5 ур. — работа на батискафе."},
    "Инкассатор": {"reqs": [40, 80, 120, 160, 200], "desc": "Профессия. Рост оплаты каждый уровень."},
    "Водитель автобуса": {"reqs": [35, 75, 105, 135, 175], "desc": "Профессия. Рост оплаты каждый уровень.\nНовые маршруты каждый уровень."},
    "Механик": {"reqs": [40, 80, 120, 160, 200], "desc": "Профессия. Постепенный тюнинг авто каждый уровень.\n5 ур. — работа на машине-эвакуаторе."},
    "Пожарный": {"reqs": [250, 200, 750, 1000, 1250], "desc": "Профессия. Рост оплаты каждый уровень."},
    "Дальнобойщик": {"reqs": [40, 80, 120, 160, 200], "desc": "Профессия. Рост оплаты каждый уровень."},
    "Доставщик": {"reqs": [100, 200, 300, 400, 500], "desc": "Профессия. Рост оплаты каждый уровень.\n5 ур. — нумерация оптимального маршрута."},
    "Почтальон": {"reqs": [140, 280, 420, 560, 700], "desc": "Профессия. +100$ за посылки на почте за уровень.\n5 ур. — работа на своём велосипеде или мотоцикле."},
    "Электрик": {"reqs": [650, 1300, 1950, 2600, 3250], "desc": "Профессия. 2 ур. — выезд на подстанции (трансформаторы).\n3 ур. — починка фонарей."},
    "Подрядчик": {"reqs": [10, 20, 30, 40, 50], "desc": "Профессия. +2% к шансу закрытия контракта за уровень."},
}

SKILLS_LIST = list(SKILLS.keys())
COLUMNS = 3

# --- Цвета ---
BG_MAIN = "#121212"
BG_CARD = "#1e1e1e"
FG_MAIN = "#ffffff"
FG_DESC = "#a0a0a0"
COLOR_ORANGE = "#f57c00"
COLOR_GREEN = "#4caf50"
ENTRY_BG = "#2a2a2a"
FONT_FAMILY = "Arial"


class SkillRow:
    def __init__(self, parent, name, app):
        self.name = name
        self.app = app
        self.reqs = SKILLS[name]["reqs"]
        self.max_level = len(self.reqs)

        saved = self.load_data()
        self.level = saved.get("level", 0)
        self.current_val = saved.get("current", 0)
        
        if "level" not in saved and self.current_val > 0:
            xp = self.current_val
            lvl = 0
            for req in self.reqs:
                if xp >= req:
                    xp -= req
                    lvl += 1
                else:
                    break
            self.level = lvl
            self.current_val = xp

        self.is_maxed = (self.level == self.max_level)
        self._updating = False

        # Задаем минимальную ширину карточки, чтобы текст не обрезался
        self.frame = tk.Frame(parent, relief="flat", borderwidth=0, bg=BG_CARD, width=380, height=90)
        self.frame.pack(fill="both", expand=True, padx=4, pady=4)
        self.frame.pack_propagate(False)

        self.icon_canvas = tk.Canvas(self.frame, width=46, height=46, bg=BG_CARD, highlightthickness=0)
        self.icon_canvas.pack(side="left", padx=(10, 10), pady=10)
        self.icon_canvas.create_oval(2, 2, 44, 44, outline=COLOR_ORANGE, width=2, tags="ring")
        self.icon_canvas.create_text(23, 23, text=name[0], fill=COLOR_ORANGE, font=(FONT_FAMILY, 16, "bold"), tags="letter")

        self.content = tk.Frame(self.frame, bg=BG_CARD)
        self.content.pack(side="left", fill="both", expand=True, pady=8, padx=(0, 8))

        top_row = tk.Frame(self.content, bg=BG_CARD)
        top_row.pack(fill="x", anchor="w")

        self.lbl_badge = tk.Label(top_row, bg="#333333", fg=FG_MAIN, font=self.get_font("bold"))
        self.lbl_badge.pack(side="left")

        self.lbl_title = tk.Label(top_row, text=name, bg=BG_CARD, fg=FG_MAIN, font=self.get_font("bold"))
        self.lbl_title.pack(side="left", padx=(8, 0))

        self.btn_help = tk.Button(top_row, text="?", command=self.show_help, bg=BG_CARD, fg=FG_DESC,
                                  relief="flat", font=self.get_font("bold"), cursor="hand2",
                                  activebackground=BG_CARD, activeforeground=COLOR_ORANGE)
        self.btn_help.pack(side="right")

        self.bottom_row = tk.Frame(self.content, bg=BG_CARD)
        self.bottom_row.pack(fill="x", anchor="w", pady=(4, 0))

        self.cmb_level = ttk.Combobox(self.bottom_row, values=list(range(0, self.max_level + 1)),
                                      width=2, state="readonly", font=self.get_font("normal"))
        self.cmb_level.pack(side="left")
        self.cmb_level.bind("<<ComboboxSelected>>", self.on_level_change)

        self.lbl_xp = tk.Label(self.bottom_row, text="Опыт:", bg=BG_CARD, fg=FG_DESC, font=self.get_font("normal"))
        self.lbl_xp.pack(side="left", padx=(4, 2))

        self.entry_cur = tk.Entry(self.bottom_row, width=4, justify="center", font=self.get_font("normal"), 
                                  bg=ENTRY_BG, fg=FG_MAIN, insertbackground=FG_MAIN, relief="flat")
        self.entry_cur.pack(side="left")
        self.entry_cur.bind("<KeyRelease>", self.on_xp_typed)
        self.entry_cur.bind("<FocusOut>", self.on_xp_focus_out)

        self.btn_minus = tk.Button(self.bottom_row, text="-", command=lambda: self.quick_change(-1),
                                   bg="#333333", fg="#ffffff", relief="flat", width=1, font=self.get_font("bold"))
        self.btn_minus.pack(side="left", padx=(2, 1))
        self.btn_plus = tk.Button(self.bottom_row, text="+", command=lambda: self.quick_change(1),
                                  bg="#333333", fg="#ffffff", relief="flat", width=1, font=self.get_font("bold"))
        self.btn_plus.pack(side="left")
        
        # Новая кнопка MAX
        self.btn_max = tk.Button(self.bottom_row, text="MAX", command=self.set_max,
                                  bg="#444444", fg=COLOR_GREEN, relief="flat", font=self.get_font("bold"))
        self.btn_max.pack(side="left", padx=(2, 0))

        self.lbl_result = tk.Label(self.bottom_row, text="", bg=BG_CARD, fg=COLOR_ORANGE, font=self.get_font("normal"))
        self.lbl_result.pack(side="left", padx=(6, 0))

        self.entry_cur.insert(0, str(self.current_val))
        self.update_ui()
        self.app.root.after(50, self.update_ui)

    def get_font(self, weight="normal"):
        return (FONT_FAMILY, int(self.app.font_scale.get()), weight)

    def update_fonts(self):
        f_norm = self.get_font("normal")
        f_bold = self.get_font("bold")
        self.lbl_badge.config(font=f_bold)
        self.lbl_title.config(font=f_bold)
        self.btn_help.config(font=f_bold)
        self.cmb_level.config(font=f_norm)
        self.lbl_xp.config(font=f_norm)
        self.entry_cur.config(font=f_norm)
        self.btn_minus.config(font=f_bold)
        self.btn_plus.config(font=f_bold)
        self.btn_max.config(font=("Arial", max(6, int(self.app.font_scale.get()) - 2), "bold"))
        self.lbl_result.config(font=f_norm)

    def set_max(self):
        self.level = self.max_level
        self.current_val = 0
        self.update_ui()
        self.app.save_all_data()

    def on_level_change(self, event):
        if self._updating: return
        self.level = int(self.cmb_level.get())
        self.current_val = 0
        self.update_ui()
        self.app.save_all_data()

    def on_xp_typed(self, event=None):
        if self._updating: return
        try:
            val_str = self.entry_cur.get()
            if not val_str: return 
            val = int(val_str)
        except ValueError:
            return
        
        if val < 0: val = 0
        self.current_val = val
        self.normalize_levels()
        self.update_ui()

    def on_xp_focus_out(self, event=None):
        self.update_ui()

    def quick_change(self, direction):
        if self.is_maxed: return
        try:
            val_str = self.entry_cur.get()
            val = int(val_str) if val_str else 0
        except ValueError:
            val = self.current_val
        
        mult = self.app.get_global_multiplier()
        new_val = val + (mult * direction)
        if new_val < 0:
            new_val = 0

        self.current_val = new_val
        self.normalize_levels()
        self.update_ui()
        self.app.save_all_data()

    def normalize_levels(self):
        self._updating = True
        while self.level < self.max_level:
            need = self.reqs[self.level]
            if self.current_val >= need:
                self.current_val -= need
                self.level += 1
            else:
                break
        if self.level >= self.max_level:
            self.level = self.max_level
            self.current_val = 0
        self.cmb_level.set(self.level)
        self._updating = False

    def update_ui(self):
        self._updating = True
        self.is_maxed = (self.level == self.max_level)
        self.lbl_badge.config(text=f" {self.level} ")

        current_text = self.entry_cur.get()
        new_text = str(self.current_val)
        if current_text != new_text:
            self.entry_cur.delete(0, tk.END)
            self.entry_cur.insert(0, new_text)

        self.entry_cur.config(
            bg=ENTRY_BG, fg=FG_MAIN, insertbackground=FG_MAIN,
            disabledbackground=ENTRY_BG, disabledforeground=FG_DESC,
            readonlybackground=ENTRY_BG,
            selectbackground=COLOR_ORANGE, selectforeground=FG_MAIN
        )

        if self.is_maxed:
            self.lbl_result.config(text="Максимальный уровень", fg=COLOR_GREEN)
            self.entry_cur.config(state="disabled")
            self.btn_plus.config(state="disabled")
            self.btn_minus.config(state="disabled")
            self.btn_max.config(state="disabled", fg="#666666")
            self.icon_canvas.itemconfig("ring", outline=COLOR_GREEN)
            self.icon_canvas.itemconfig("letter", fill=COLOR_GREEN)
        else:
            self.entry_cur.config(state="normal")
            self.btn_plus.config(state="normal")
            self.btn_minus.config(state="normal")
            self.btn_max.config(state="normal", fg=COLOR_GREEN)
            need = self.reqs[self.level]
            remaining = need - self.current_val
            mult = self.app.get_global_multiplier()
            actions = math.ceil(remaining / mult) if remaining > 0 else 0
            self.lbl_result.config(text=f"ещё {remaining} (д: {actions})", fg=COLOR_ORANGE)
            self.icon_canvas.itemconfig("ring", outline=COLOR_ORANGE)
            self.icon_canvas.itemconfig("letter", fill=COLOR_ORANGE)
        self._updating = False

    def show_help(self):
        text = SKILLS[self.name]["desc"]
        reqs_text = "\n".join([f"  с {i} на {i+1}: {r} опыта" for i, r in enumerate(self.reqs)])
        msg = f"{text}\n\nТребования:\n{reqs_text}"
        messagebox.showinfo(f"Что даёт: {self.name}", msg, parent=self.app.root)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(self.name, {})
            except Exception:
                return {}
        return {}

    def get_save_dict(self):
        return {"level": self.level, "current": self.current_val}


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Доступные профессии")
        self.root.geometry("1350x850")
        self.root.minsize(1300, 500) # Увеличили минимальную ширину окна
        self.root.configure(bg=BG_MAIN)

        self.rows = {}
        self._loaded = False
        self.font_scale = tk.IntVar(value=9)

        saved_globals = self._load_globals()
        self.global_vip = tk.BooleanVar(value=saved_globals.get("vip", False))
        self.global_x2 = tk.BooleanVar(value=saved_globals.get("x2", False))
        if "font_size" in saved_globals:
            self.font_scale.set(saved_globals["font_size"])

        header = tk.Frame(root, bg=BG_MAIN, pady=10)
        header.pack(fill="x", padx=20)

        tk.Label(header, text="Доступные профессии", bg=BG_MAIN, fg=FG_MAIN, font=(FONT_FAMILY, 18, "bold")).pack(side="left")
        right = tk.Frame(header, bg=BG_MAIN)
        right.pack(side="right")

        tk.Label(right, text="Шрифт:", bg=BG_MAIN, fg=FG_DESC, font=(FONT_FAMILY, 9)).pack(side="left", padx=(0, 5))
        scale_font = tk.Scale(right, from_=7, to=16, orient="horizontal", 
                              variable=self.font_scale, command=self.on_font_change,
                              bg=BG_MAIN, fg=FG_MAIN, highlightthickness=0, troughcolor="#333",
                              length=100, showvalue=True)
        scale_font.pack(side="left", padx=(0, 15))

        tk.Checkbutton(right, text="VIP (×2)", variable=self.global_vip, command=self.on_global_change,
                       bg=BG_MAIN, fg=FG_DESC, selectcolor=BG_CARD, activebackground=BG_MAIN, activeforeground=FG_MAIN,
                       font=(FONT_FAMILY, 9)).pack(side="left", padx=10)
        tk.Checkbutton(right, text="x2 (×2)", variable=self.global_x2, command=self.on_global_change,
                       bg=BG_MAIN, fg=FG_DESC, selectcolor=BG_CARD, activebackground=BG_MAIN, activeforeground=FG_MAIN,
                       font=(FONT_FAMILY, 9)).pack(side="left", padx=10)

        tk.Button(right, text="Сохранить", command=self.manual_save, bg=COLOR_ORANGE, fg=FG_MAIN, font=(FONT_FAMILY, 9, "bold"), relief="flat").pack(side="left", padx=10)
        tk.Button(right, text="Сбросить ВСЁ", command=self.reset_all, bg="#444", fg=FG_MAIN, font=(FONT_FAMILY, 9, "bold"), relief="flat").pack(side="left")

        canvas = tk.Canvas(root, bg=BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=BG_MAIN)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        scrollbar.pack(side="right", fill="y")

        # Устанавливаем минимальную ширину колонок, чтобы карточки не сжимались
        for i in range(COLUMNS):
            self.scrollable_frame.grid_columnconfigure(i, weight=1, uniform="col", minsize=410)

        for index, skill in enumerate(SKILLS_LIST):
            row_idx = index // COLUMNS
            col_idx = index % COLUMNS
            cell = tk.Frame(self.scrollable_frame, bg=BG_MAIN)
            cell.grid(row=row_idx, column=col_idx, sticky="nsew")
            row = SkillRow(cell, skill, self)
            self.rows[skill] = row

        self._loaded = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_font_change(self, event=None):
        new_size = int(self.font_scale.get())
        style = ttk.Style()
        style.configure("TCombobox", font=(FONT_FAMILY, new_size))
        for row in self.rows.values():
            row.update_fonts()
        self.save_all_data()

    def get_global_multiplier(self):
        mult = 1
        if self.global_vip.get(): mult *= 2
        if self.global_x2.get(): mult *= 2
        return mult

    def _load_globals(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("__globals__", {})
            except Exception:
                return {}
        return {}

    def on_global_change(self):
        for row in self.rows.values():
            row.update_ui()
        self.save_all_data()

    def manual_save(self):
        success = self.save_all_data()
        if success:
            messagebox.showinfo("Сохранено", f"Данные успешно записаны в:\n{DATA_FILE}", parent=self.root)
        else:
            ans = messagebox.askyesno("Ошибка доступа", 
                "Не удалось сохранить файл в папку со скриптом.\n"
                "Возможно, у папки нет прав на запись.\n\n"
                "Запустить программу от имени Администратора?", parent=self.root)
            if ans:
                try:
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                except Exception:
                    pass
                self.root.destroy()

    def save_all_data(self):
        if not self._loaded:
            return False
            
        data = {
            "__globals__": {
                "vip": self.global_vip.get(),
                "x2": self.global_x2.get(),
                "font_size": int(self.font_scale.get())
            }
        }
        for name, row in self.rows.items():
            data[name] = row.get_save_dict()
            
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False

    def on_close(self):
        self.save_all_data()
        self.root.destroy()

    def reset_all(self):
        if messagebox.askyesno("Сброс", "Точно удалить все данные?", parent=self.root):
            if os.path.exists(DATA_FILE):
                try:
                    os.remove(DATA_FILE)
                except Exception:
                    pass
            self.root.destroy()
            os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    
    style.configure("TCombobox", 
        fieldbackground=ENTRY_BG, background="#333", foreground=FG_MAIN, arrowcolor=FG_MAIN,
        bordercolor=ENTRY_BG, lightcolor=ENTRY_BG, darkcolor=ENTRY_BG
    )
    style.map("TCombobox", 
        fieldbackground=[("readonly", ENTRY_BG)], foreground=[("readonly", FG_MAIN)],
        background=[("readonly", "#333")], selectbackground=[("readonly", ENTRY_BG)], selectforeground=[("readonly", FG_MAIN)]
    )
    style.configure("Vertical.TScrollbar", background="#333", bordercolor=BG_MAIN, arrowcolor=FG_MAIN, troughcolor=BG_MAIN)
    
    root.option_add("*TCombobox*Listbox.background", ENTRY_BG)
    root.option_add("*TCombobox*Listbox.foreground", FG_MAIN)
    root.option_add("*TCombobox*Listbox.selectBackground", COLOR_ORANGE)
    root.option_add("*TCombobox*Listbox.selectForeground", FG_MAIN)
    
    app = App(root)
    root.mainloop()