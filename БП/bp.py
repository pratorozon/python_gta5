import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import threading
import time
import traceback
import tempfile

# ---------- Пути ----------
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

def _pick_data_dir():
    candidates = [SCRIPT_DIR]
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(os.path.join(appdata, "BP_Tracker"))
    candidates.append(os.path.join(os.path.expanduser("~"), ".bp_tracker"))
    candidates.append(tempfile.gettempdir())

    for d in candidates:
        try:
            os.makedirs(d, exist_ok=True)
            test = os.path.join(d, ".write_test")
            with open(test, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(test)
            return d
        except Exception:
            continue
    return tempfile.gettempdir()

DATA_DIR = _pick_data_dir()
DATA_FILE = os.path.join(DATA_DIR, "bp_config.json")
ERROR_LOG = os.path.join(DATA_DIR, "error.log")

# ---------- Цвета (тема "ocean") ----------
BG_MAIN       = "#0b1c2c"
BG_CARD       = "#10293d"
FG_MAIN       = "#e6f1f8"
FG_MUTED      = "#8fb3c9"
BORDER        = "#1e3a52"
BTN_BG        = "#173850"
BTN_HOVER     = "#204a68"
ACCENT        = "#35b1ff"
PROGRESS_BG   = "#1a3448"
PROGRESS_FG   = "#5fb8e8"
GREEN         = "#4caf50"
ORANGE        = "#ffb74d"
RED           = "#ff6b6b"
ENTRY_BG      = "#0b1c2c"
FONT          = "Segoe UI"

# ---------- Данные ----------
DATA = [
    ("Легкие", "Купить лотерейный билет", "лотерея", 1, None, None),
    ("Легкие", "Посетить любой сайт в браузере", "сайт", 1, None, None),
    ("Легкие", "Поставить лайк любой анкете в Match", "лайк в Match", 1, None, None),
    ("Легкие", "Зайти в любой канал в Brawl", "Brawl (рация)", 1, None, None),
    ("Легкие", "Добавить 5 видео в кинотеатре", "кинотеатр", 1, 5, None),
    ("Легкие", "Арендовать киностудию", "киностудия", 2, None, None),
    ("Легкие", "Забить 2 гола в футболе", "футбол", 1, 2, None),
    ("Легкие", "Починить деталь в автосервисе", "автосервис (СТО)", 1, None, None),
    ("Легкие", "Успешная тренировка в тире", "тир", 1, None, None),
    ("Легкие", "Поиграть 1 минуту в настольный теннис", "пинг-понг (теннис)", 1, None, 60),
    ("Легкие", "10 действий на ферме", "ферма", 1, 10, None),
    ("Легкие", "Нули в казино", "Нули в казино", 2, None, None),
    ("Легкие", "Ставка межсерверное колесо", "ставка в колесе", 3, None, None),
    ("Легкие", "Забросить 2 мяча в баскетболе", "баскетбол", 1, 2, None),
    ("Легкие", "Поиграть 1 минуту в большой теннис", "большой теннис (тенннис)", 1, None, 60),
    ("Легкие", "Победить в дартс", "дартс", 1, None, None),
    ("Легкие", "Забить 10 голов в волейболе", "волейбол", 1, None, 60),
    ("Легкие", "Сделать платёж по лизингу", "платёж по лизингу", 1, None, None),

    ("Среднее", "25 действий на стройке", "стройка", 2, 25, None),
    ("Среднее", "25 действий в порту", "порт", 2, 25, None),
    ("Среднее", "25 действий в шахте", "шахта", 2, 25, None),
    ("Среднее", "2 круга на любом маршруте автобусника", "авторбус", 2, 2, None),
    ("Среднее", "Выполнить 2 квеста любых клубов", "задание клуба", 4, None, None),
    ("Среднее", "Проехать 1 станцию на метро", "метро", 2, None, None),
    ("Среднее", "Поймать 20 рыб", "рыбалка", 4, 20, None),
    ("Среднее", "Кинуть мяч питомцу 15 раз", "Кинуть мяч", 2, 15, None),
    ("Среднее", "15 выполненных питомцем команд", "дрессировка", 2, 15, None),
    ("Среднее", "20 подходов в тренажерном зале", "тренажерный зал (ТЗ)", 1, 20, None),
    ("Среднее", "Выкопать 1 сокровище", "сокровище (клад)", 1, None, None),
    ("Среднее", "5 раз снять 100% шкуру с животных", "охота", 2, 5, None),
    ("Среднее", "Выполнить 3 заказа дальнобойщиком", "дальнобойщик", 2, 3, None),

    ("Совместные", "Сыграть в мафию в казино", "мафия", 3, None, None),
    ("Совместные", "Выиграть гонку в картинге", "картинг", 1, None, None),
    ("Совместные", "Проехать 1 уличную гонку (через тлф. ставка от 1000$)", "гонка", 1, None, None),
    ("Совместные", "Выиграть 5 игр в тренировочном комплексе со ставкой (от 100$)", "тренировочный комплекс (ТК)", 1, 5, None),
    ("Совместные", "Выиграть 3 любых игры на арене со ставкой (от 100$)", "арена", 1, 3, None),
    ("Совместные", "3 победы в Дэнс Баттлах", "Дэнс Баттлах (танцы)", 2, 3, None),
    ("Совместные", "Победить в армрестлинге", "армрестлинг", 1, None, None),
    ("Совместные", "Починка авто другому игроку", "автосервис (механик)", 2, None, None),

    ("Долго", "10 посылок на почте", "почта", 1, 10, 600),
    ("Долго", "Прокрутить за DP серебряный или золотой кейс", "открыть кейс", 10, None, None),
    ("Долго", "Заказ материалов для бизнеса вручную (просто прожать вкл/выкл)", "Заказ материалов для бизнеса", 1, None, None),
    ("Долго", "Потушить 25 «огоньков» пожарным", "пожарный", 1, 25, None),
    ("Долго", "Два раза оплатить смену внешности у хирурга в EMS", "смена внешности", 2, 2, None),
    ("Долго", "Принять участие в двух аирдропах", "аирдроп", 4, None, None),

    ("Фракционные", "7 закрашенных граффити", "граффити", 1, 7, None),
    ("Фракционные", "Сдать 5 контрабанды", "контрабанда", 2, 5, None),
    ("Фракционные", "Участие в каптах/бизварах", "капт  ибизвар", 1, None, None),
    ("Фракционные", "Сдать Хаммер с ВЗХ", "ВЗХ", 3, None, None),
    ("Фракционные", "5 выданных медкарт в EMS", "выдать 5 медкарт (EMS)", 2, 5, None),
    ("Фракционные", "Закрыть 15 вызовов в EMS", "15 вызовов (EMS)", 2, 15, None),
    ("Фракционные", "Отредактировать 40 объявлений в WN", "40 объявлений в WN", 2, 40, None),
    ("Фракционные", "Взломать 15 замков на ограбах домов или автоугонах", "ограбление домов и угон авто", 2, 15, None),
    ("Фракционные", "Закрыть 5 кодов в силовых структурах", "5 кодов", 2, 5, None),
    ("Фракционные", "Поставить на учет 2 автомобиля (для LSPD)", "2 автомобиля на учёт (LSPD)", 1, 2, None),
    ("Фракционные", "Произвести 1 арест в КПЗ", "1 арест в (КПЗ)", 1, None, None),
    ("Фракционные", "Выкупить двух человек из КПЗ", "Выкупить двух человек из (КПЗ)", 2, 2, None),
    ("Фракционные", "Посадить траву в теплице", "трава в теплице", 4, None, None),
    ("Фракционные", "Запустить переработку обезболивающих в лаборатории", "обезбол в лаборатории", 4, None, None),
]

SECTIONS = ["Легкие", "Среднее", "Совместные", "Долго", "Фракционные"]


def log_error(exc_info_text):
    try:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 60 + "\n")
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
            f.write(exc_info_text)
    except Exception:
        pass


class Task:
    def __init__(self, section, full, short, bonus, limit, timer):
        self.section = section
        self.full = full
        self.short = short
        self.bonus = bonus
        self.limit = limit
        self.timer = timer
        self.progress = 0
        self.done_today = False
        self.favorite = False
        self.timer_running = False
        self.timer_left = 0
        self.timer_thread = None

    def need(self):
        return self.limit if self.limit else 1

    def reset_day(self):
        self.progress = 0
        self.done_today = False

    def key(self):
        return f"{self.section}||{self.short}"

    def to_dict(self):
        return {"progress": self.progress,
                "done": self.done_today,
                "favorite": self.favorite}

    def from_dict(self, d):
        self.progress = int(d.get("progress", 0))
        self.done_today = bool(d.get("done", False))
        self.favorite = bool(d.get("favorite", False))


class Card(tk.Frame):
    def __init__(self, parent, task, app):
        super().__init__(parent, bg=BG_CARD, highlightbackground=BORDER,
                         highlightthickness=1, bd=0)
        self.task = task
        self.app = app
        self._updating = False
        self._hover = False
        self._children = []
        self.var_cur = None
        self.entry = None
        self.btn_action = None
        self.btn_timer = None
        self.lbl_timer = None
        self.title_lbl = None
        self._build()
        self._sync_from_task()
        self._bind_hover_all()

    def _build(self):
        pad = 12
        top = tk.Frame(self, bg=BG_CARD)
        top.pack(fill="x", padx=pad, pady=(pad, 4))

        self._add_child(top)
        tk.Label(top, text=self.task.section.upper(), bg=BG_CARD, fg=FG_MUTED,
                 font=(FONT, 8, "bold")).pack(side="left")

        self.var_fav = tk.BooleanVar(value=self.task.favorite)
        cb = tk.Checkbutton(top, text="★", variable=self.var_fav,
                            command=self._toggle_fav,
                            bg=BG_CARD, fg=ORANGE, selectcolor=BG_CARD,
                            activebackground=BG_CARD, activeforeground=ORANGE,
                            font=(FONT, 12, "bold"), bd=0, highlightthickness=0,
                            cursor="hand2")
        cb.pack(side="right")
        self._add_child(cb)
        self.chk_fav = cb

        self.title_lbl = tk.Label(self, text=self.task.full, bg=BG_CARD, fg=ACCENT,
                                  font=(FONT, 11, "bold"), wraplength=280,
                                  justify="left", anchor="w")
        self.title_lbl.pack(fill="x", padx=pad, pady=(0, 2))
        self._add_child(self.title_lbl)

        short_lbl = tk.Label(self, text=f"({self.task.short})", bg=BG_CARD,
                             fg=FG_MUTED, font=(FONT, 9), anchor="w")
        short_lbl.pack(fill="x", padx=pad, pady=(0, 6))
        self._add_child(short_lbl)

        row_badge = tk.Frame(self, bg=BG_CARD)
        row_badge.pack(fill="x", padx=pad, pady=(0, 6))
        self._add_child(row_badge)

        self.lbl_bonus = tk.Label(row_badge, text="", bg=ACCENT, fg="#04121e",
                                  font=(FONT, 9, "bold"), padx=8, pady=3)
        self.lbl_bonus.pack(side="left")
        self._add_child(self.lbl_bonus)

        self.lbl_status = tk.Label(row_badge, text="", bg=BG_CARD, fg=GREEN,
                                   font=(FONT, 9, "bold"))
        self.lbl_status.pack(side="left", padx=8)
        self._add_child(self.lbl_status)

        prog_frame = tk.Frame(self, bg=PROGRESS_BG, height=6)
        prog_frame.pack(fill="x", padx=pad, pady=(0, 2))
        prog_frame.pack_propagate(False)
        self.prog_bar = tk.Frame(prog_frame, bg=PROGRESS_FG, height=6)
        self.prog_bar.place(x=0, y=0, relheight=1, relwidth=0)
        self._add_child(prog_frame)
        self._add_child(self.prog_bar)

        self.lbl_progress = tk.Label(self, text="", bg=BG_CARD, fg=FG_MUTED,
                                     font=(FONT, 8), anchor="w")
        self.lbl_progress.pack(fill="x", padx=pad, pady=(0, 6))
        self._add_child(self.lbl_progress)

        row_ctrl = tk.Frame(self, bg=BG_CARD)
        row_ctrl.pack(fill="x", padx=pad, pady=(0, pad))
        self._add_child(row_ctrl)

        need = self.task.need()
        if need > 1:
            self.var_cur = tk.StringVar(value=str(self.task.progress))
            b_minus = tk.Button(row_ctrl, text="−1", command=lambda: self._change(-1),
                                bg=BTN_BG, fg=FG_MAIN, relief="flat",
                                font=(FONT, 9, "bold"), width=3, cursor="hand2",
                                activebackground=BTN_HOVER, activeforeground=FG_MAIN,
                                bd=0)
            b_minus.pack(side="left", padx=(0, 4))
            self._add_child(b_minus)

            self.entry = tk.Entry(row_ctrl, textvariable=self.var_cur, width=5,
                                  justify="center", font=(FONT, 10, "bold"),
                                  bg=ENTRY_BG, fg=FG_MAIN, insertbackground=FG_MAIN,
                                  relief="flat", bd=0, highlightthickness=1,
                                  highlightbackground=BORDER, highlightcolor=ACCENT)
            self.entry.pack(side="left", ipady=3)
            self.entry.bind("<Return>", lambda e: self._apply_entry())
            self.entry.bind("<FocusOut>", lambda e: self._apply_entry())
            self._add_child(self.entry)

            b_plus = tk.Button(row_ctrl, text="+1", command=lambda: self._change(1),
                               bg=BTN_BG, fg=FG_MAIN, relief="flat",
                               font=(FONT, 9, "bold"), width=3, cursor="hand2",
                               activebackground=BTN_HOVER, activeforeground=FG_MAIN,
                               bd=0)
            b_plus.pack(side="left", padx=(4, 0))
            self._add_child(b_plus)
        else:
            self.btn_action = tk.Button(row_ctrl, text="Выполнить",
                                        command=self._do_single,
                                        bg=BTN_BG, fg=FG_MAIN, relief="flat",
                                        font=(FONT, 9, "bold"), cursor="hand2",
                                        activebackground=BTN_HOVER,
                                        activeforeground=FG_MAIN, bd=0)
            self.btn_action.pack(side="left")
            self._add_child(self.btn_action)

        if self.task.timer:
            self.btn_timer = tk.Button(row_ctrl, text=f"⏱ {self.task.timer // 60} мин",
                                       command=self._toggle_timer,
                                       bg=BTN_BG, fg=ORANGE, relief="flat",
                                       font=(FONT, 9, "bold"), cursor="hand2",
                                       activebackground=BTN_HOVER,
                                       activeforeground=ORANGE, bd=0)
            self.btn_timer.pack(side="right")
            self._add_child(self.btn_timer)

            self.lbl_timer = tk.Label(self, text="", bg=BG_CARD, fg=ORANGE,
                                      font=(FONT, 9, "bold"))
            self.lbl_timer.pack(fill="x", padx=pad, pady=(0, 4))
            self._add_child(self.lbl_timer)

    def _add_child(self, w):
        self._children.append(w)

    def _bind_hover_all(self):
        def on_enter(_e=None):
            self._set_hover(True)
        def on_leave(_e=None):
            try:
                x, y = self.winfo_pointerxy()
                under = self.winfo_containing(x, y)
                w = under
                while w is not None:
                    if w == self:
                        return
                    w = w.master
            except Exception:
                pass
            self._set_hover(False)

        for w in [self] + self._children:
            try:
                w.bind("<Enter>", on_enter, add="+")
                w.bind("<Leave>", on_leave, add="+")
            except Exception:
                pass

    def _set_hover(self, on):
        if self._hover == on:
            return
        self._hover = on
        if on:
            border = GREEN if self.task.done_today else ORANGE
            self.configure(highlightbackground=border, highlightcolor=border)
        else:
            self.configure(highlightbackground=BORDER, highlightcolor=BORDER)

    def _toggle_fav(self):
        self.task.favorite = self.var_fav.get()
        self.app.save_all_data()
        if self.app.active_tab == "favorite" and not self.task.favorite:
            self.app.refresh_views()

    def _change(self, delta):
        if self._updating:
            return
        try:
            cur = int(self.var_cur.get())
        except ValueError:
            cur = self.task.progress
        self._apply_value(max(0, cur + delta))

    def _apply_entry(self):
        try:
            val = int(self.var_cur.get())
        except ValueError:
            val = self.task.progress
        self._apply_value(max(0, val))

    def _apply_value(self, val):
        need = self.task.need()
        if not self.task.done_today and val >= need:
            val = need
            self.task.done_today = True
        self.task.progress = min(val, need)
        self._sync_from_task()
        self.app.save_all_data()
        self.app.refresh_counters()
        # если включён фильтр "Скрыть готовое" — карточка должна исчезнуть
        if self.task.done_today and self.app.hide_done.get():
            self.app.refresh_views()

    def _do_single(self):
        if self.task.done_today:
            return
        self.task.progress = self.task.need()
        self.task.done_today = True
        self._sync_from_task()
        self.app.save_all_data()
        self.app.refresh_counters()
        if self.app.hide_done.get():
            self.app.refresh_views()

    def _sync_from_task(self):
        self._updating = True
        try:
            mult = self.app.get_multiplier()
            self.lbl_bonus.configure(text=f"+{self.task.bonus * mult} BP")

            need = self.task.need()
            done = self.task.done_today
            prog = self.task.progress

            if done:
                self.title_lbl.configure(text=f"✓ {self.task.full}", fg=GREEN)
                self.lbl_status.configure(text="✓ выполнено", fg=GREEN)
            else:
                self.title_lbl.configure(text=self.task.full, fg=ACCENT)
                self.lbl_status.configure(text="")

            if need > 1:
                self.lbl_progress.configure(text=f"Прогресс: {prog} / {need}")
                self.prog_bar.place_configure(relwidth=min(1.0, prog / need))
            else:
                if done:
                    self.lbl_progress.configure(text="Бонус получен сегодня")
                    self.prog_bar.place_configure(relwidth=1.0)
                else:
                    self.lbl_progress.configure(text="Разовое задание")
                    self.prog_bar.place_configure(relwidth=0.0)

            if self.btn_action:
                if done:
                    self.btn_action.configure(text="Готово ✓", state="disabled",
                                              bg=BG_CARD, fg=GREEN)
                else:
                    self.btn_action.configure(text="Выполнить", state="normal",
                                              bg=BTN_BG, fg=FG_MAIN)

            if self.var_cur is not None and self.entry is not None:
                if self.var_cur.get() != str(prog):
                    self.var_cur.set(str(prog))
                self.entry.configure(state="disabled" if done else "normal",
                                     bg=ENTRY_BG if not done else BG_CARD,
                                     fg=FG_MAIN if not done else FG_MUTED)

            if self._hover:
                self._set_hover(False)
                self._set_hover(True)
        finally:
            self._updating = False

    def _toggle_timer(self):
        if self.task.timer_running:
            return
        self.task.timer_running = True
        self.task.timer_left = self.task.timer
        if self.task.timer_thread and self.task.timer_thread.is_alive():
            return
        self.task.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self.task.timer_thread.start()

    def _run_timer(self):
        while self.task.timer_left > 0 and self.task.timer_running:
            time.sleep(1)
            self.task.timer_left -= 1
        if self.task.timer_running:
            self.task.timer_running = False
            self._play_sound()
        try:
            self.after(0, self.app.refresh_timers)
        except Exception:
            pass

    def _play_sound(self):
        try:
            import winsound
            winsound.Beep(880, 350)
            winsound.Beep(1200, 350)
        except Exception:
            try:
                self.bell()
            except Exception:
                pass


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("BP-очки — трекер бонусов")
        self.root.geometry("1250x820")
        self.root.minsize(1000, 600)
        self.root.configure(bg=BG_MAIN)

        self.tasks = [Task(*row) for row in DATA]
        self.cards = {}
        self.task_to_cell = {}

        self.vip = tk.BooleanVar(value=False)
        self.x2 = tk.BooleanVar(value=False)
        self.hide_done = tk.BooleanVar(value=False)  # <— фильтр готового
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *a: self._safe_refresh_views())
        self.active_tab = "favorite"

        self._build_header()
        self._build_tabs()
        self._build_content()
        self._load_data()
        self._build_all_cards()

        self.switch_tab("favorite")
        self.refresh_counters()
        self._tick_timers()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _safe_refresh_views(self):
        try:
            self.refresh_views()
        except Exception:
            log_error(traceback.format_exc())

    def _safe_refresh_counters(self):
        try:
            self.refresh_counters()
        except Exception:
            log_error(traceback.format_exc())

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG_MAIN)
        header.pack(fill="x", padx=20, pady=(16, 8))

        left = tk.Frame(header, bg=BG_MAIN)
        left.pack(side="left")
        tk.Label(left, text="BP-очки", bg=BG_MAIN, fg=FG_MAIN,
                 font=(FONT, 20, "bold")).pack(side="left")

        self.badge_fav = tk.Label(left, text="★ 0 BP", bg=ACCENT, fg="#04121e",
                                  font=(FONT, 10, "bold"), padx=10, pady=4)
        self.badge_fav.pack(side="left", padx=(12, 0))
        self.badge_all = tk.Label(left, text="Всего: 0 BP", bg=GREEN, fg="#04121e",
                                  font=(FONT, 10, "bold"), padx=10, pady=4)
        self.badge_all.pack(side="left", padx=(8, 0))

        right = tk.Frame(header, bg=BG_MAIN)
        right.pack(side="right")

        tk.Label(right, text="Поиск:", bg=BG_MAIN, fg=FG_MUTED,
                 font=(FONT, 9)).pack(side="left", padx=(0, 4))
        tk.Entry(right, textvariable=self.search, width=26,
                 bg=ENTRY_BG, fg=FG_MAIN, insertbackground=FG_MAIN,
                 relief="flat", bd=0, highlightthickness=1,
                 highlightbackground=BORDER, highlightcolor=ACCENT,
                 font=(FONT, 10)).pack(side="left", ipady=4, padx=(0, 12))

        for txt, var in (("VIP ×2", self.vip), ("x2 ×2", self.x2)):
            tk.Checkbutton(right, text=txt, variable=var,
                           command=self.on_mult_change,
                           bg=BG_MAIN, fg=FG_MUTED, selectcolor=BG_CARD,
                           activebackground=BG_MAIN, activeforeground=FG_MAIN,
                           font=(FONT, 10, "bold"), bd=0,
                           highlightthickness=0).pack(side="left", padx=4)

        # ---- кнопка "Скрыть готовое" (переключатель) ----
        self.btn_hide = tk.Button(right, text="Скрыть готовое",
                                  command=self.toggle_hide_done,
                                  bg=BTN_BG, fg=FG_MAIN, relief="flat", bd=0,
                                  font=(FONT, 10, "bold"), cursor="hand2",
                                  activebackground=BTN_HOVER, activeforeground=FG_MAIN,
                                  padx=12, pady=6)
        self.btn_hide.pack(side="left", padx=(12, 4))

        self._mk_btn(right, "Новый день", self.reset_day).pack(side="left", padx=4)
        self._mk_btn(right, "Сброс БП", self.reset_bp, bg="#a33", fg="#fff").pack(side="left", padx=4)
        self._mk_btn(right, "Сохранить", self.save_manual).pack(side="left", padx=4)

        # применить сохранённое значение к кнопке
        self._update_hide_button()

    def _mk_btn(self, parent, text, cmd, bg=BTN_BG, fg=FG_MAIN):
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=fg, relief="flat", bd=0,
                         font=(FONT, 10, "bold"), cursor="hand2",
                         activebackground=BTN_HOVER, activeforeground=fg,
                         padx=12, pady=6)

    def _update_hide_button(self):
        if self.hide_done.get():
            self.btn_hide.configure(text="Показать готовое",
                                    bg=ORANGE, fg="#04121e",
                                    activebackground="#ffc46b",
                                    activeforeground="#04121e")
        else:
            self.btn_hide.configure(text="Скрыть готовое",
                                    bg=BTN_BG, fg=FG_MAIN,
                                    activebackground=BTN_HOVER,
                                    activeforeground=FG_MAIN)

    def toggle_hide_done(self):
        self.hide_done.set(not self.hide_done.get())
        self._update_hide_button()
        self._safe_refresh_views()
        self.save_all_data()

    def _build_tabs(self):
        bar = tk.Frame(self.root, bg=BG_MAIN)
        bar.pack(fill="x", padx=20, pady=(4, 8))
        self.tab_buttons = {}

        def make(text, key):
            b = tk.Button(bar, text=text, relief="flat", bd=0,
                          bg=BTN_BG, fg=FG_MUTED,
                          font=(FONT, 10, "bold"), cursor="hand2",
                          padx=14, pady=6,
                          activebackground=BTN_HOVER, activeforeground=FG_MAIN,
                          command=lambda k=key: self.switch_tab(k))
            b.pack(side="left", padx=(0, 6))
            self.tab_buttons[key] = b

        make("★ Избранное", "favorite")
        make("Все", "all")
        for s in SECTIONS:
            make(s, s)

    def switch_tab(self, key):
        self.active_tab = key
        for k, b in self.tab_buttons.items():
            if k == key:
                b.configure(bg=ACCENT, fg="#04121e")
            else:
                b.configure(bg=BTN_BG, fg=FG_MUTED)
        self._safe_refresh_views()

    def _build_content(self):
        wrapper = tk.Frame(self.root, bg=BG_MAIN)
        wrapper.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.canvas = tk.Canvas(wrapper, bg=BG_MAIN, highlightthickness=0)
        vsb = ttk.Scrollbar(wrapper, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=BG_MAIN)

        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self.window_id, width=e.width))
        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"))

        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.COLUMNS = 3
        for i in range(self.COLUMNS):
            self.inner.grid_columnconfigure(i, weight=1, uniform="col", minsize=360)

    def _build_all_cards(self):
        for idx, task in enumerate(self.tasks):
            r, c = divmod(idx, self.COLUMNS)
            cell = tk.Frame(self.inner, bg=BG_MAIN)
            cell.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
            card = Card(cell, task, self)
            card.pack(fill="both", expand=True)
            self.cards[task] = card
            self.task_to_cell[task] = cell

        self.empty_label = tk.Label(self.inner, text="Ничего не найдено.",
                                    bg=BG_MAIN, fg=FG_MUTED, font=(FONT, 12))

    def refresh_views(self):
        q = self.search.get().strip().lower()
        hide = self.hide_done.get()

        def match(t):
            if not q:
                return True
            return q in t.full.lower() or q in t.short.lower()

        visible_tasks = []
        for task in self.tasks:
            if self.active_tab == "favorite":
                ok = task.favorite
            elif self.active_tab == "all":
                ok = True
            else:
                ok = (task.section == self.active_tab)
            ok = ok and match(task)
            # --- фильтр "Скрыть готовое" ---
            if ok and hide and task.done_today:
                ok = False

            cell = self.task_to_cell[task]
            if ok:
                if not cell.winfo_ismapped():
                    cell.grid()
                visible_tasks.append(task)
            else:
                if cell.winfo_ismapped():
                    cell.grid_remove()

        for pos, task in enumerate(visible_tasks):
            r, c = divmod(pos, self.COLUMNS)
            self.task_to_cell[task].grid(row=r, column=c)

        if not visible_tasks:
            self.empty_label.grid(row=0, column=0, columnspan=self.COLUMNS, pady=60)
        else:
            self.empty_label.grid_remove()

        self.canvas.yview_moveto(0)
        self.refresh_counters()

    def refresh_counters(self):
        mult = self.get_multiplier()
        fav_bp = sum(t.bonus for t in self.tasks if t.favorite and t.done_today) * mult
        all_bp = sum(t.bonus for t in self.tasks if t.done_today) * mult
        self.badge_fav.configure(text=f"★ {fav_bp} BP")
        self.badge_all.configure(text=f"Всего: {all_bp} BP")
        for card in self.cards.values():
            try:
                card._sync_from_task()
            except tk.TclError:
                pass

    def refresh_timers(self):
        for task, card in self.cards.items():
            if not card.lbl_timer:
                continue
            if not self.task_to_cell[task].winfo_ismapped():
                continue
            t = task
            try:
                if t.timer_running and t.timer_left > 0:
                    m, s = divmod(t.timer_left, 60)
                    card.lbl_timer.configure(text=f"⏱ {m:02d}:{s:02d}", fg=ORANGE)
                elif t.timer_running and t.timer_left == 0:
                    card.lbl_timer.configure(text="⏱ время вышло", fg=RED)
                else:
                    card.lbl_timer.configure(text="")
            except tk.TclError:
                pass

    def _tick_timers(self):
        try:
            self.refresh_timers()
        except Exception:
            log_error(traceback.format_exc())
        self.root.after(500, self._tick_timers)

    def get_multiplier(self):
        m = 1
        if self.vip.get():
            m *= 2
        if self.x2.get():
            m *= 2
        return m

    def on_mult_change(self):
        self._safe_refresh_counters()
        self.save_all_data()

    def _load_data(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            log_error(traceback.format_exc())
            return

        self.vip.set(bool(data.get("vip", False)))
        self.x2.set(bool(data.get("x2", False)))
        self.hide_done.set(bool(data.get("hide_done", False)))
        saved = data.get("tasks", {})
        for t in self.tasks:
            if t.key() in saved:
                try:
                    t.from_dict(saved[t.key()])
                except Exception:
                    log_error(traceback.format_exc())

    def save_all_data(self):
        data = {"vip": self.vip.get(),
                "x2": self.x2.get(),
                "hide_done": self.hide_done.get(),
                "tasks": {}}
        for t in self.tasks:
            data["tasks"][t.key()] = t.to_dict()
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            log_error(traceback.format_exc())
            return False

    def save_manual(self):
        if self.save_all_data():
            messagebox.showinfo("Сохранено",
                                f"Данные записаны в:\n{DATA_FILE}",
                                parent=self.root)
        else:
            messagebox.showerror("Ошибка",
                                 f"Не удалось сохранить файл.\nПодробности в:\n{ERROR_LOG}",
                                 parent=self.root)

    def reset_day(self):
        if not messagebox.askyesno("Новый день",
                                   "Сбросить прогресс и отметки «выполнено» у всех заданий?\n"
                                   "Избранное останется.",
                                   parent=self.root):
            return
        for t in self.tasks:
            t.reset_day()
        self.save_all_data()
        self._safe_refresh_views()

    def reset_bp(self):
        if not messagebox.askyesno("Сброс БП",
                                   "Сбросить весь прогресс и отметки «выполнено»?\n"
                                   "Избранное и множители останутся.",
                                   parent=self.root):
            return
        for t in self.tasks:
            t.reset_day()
        self.save_all_data()
        self._safe_refresh_views()

    def on_close(self):
        self.save_all_data()
        self.root.destroy()


def main():
    try:
        root = tk.Tk()
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Vertical.TScrollbar",
                        background="#173850", troughcolor=BG_MAIN,
                        bordercolor=BG_MAIN, arrowcolor=FG_MAIN,
                        darkcolor="#173850", lightcolor="#173850")
        App(root)
        root.mainloop()
    except Exception:
        tb = traceback.format_exc()
        log_error(tb)
        try:
            r = tk.Tk()
            r.title("Ошибка")
            r.geometry("720x480")
            r.configure(bg="#1e1e1e")
            txt = tk.Text(r, bg="#111", fg="#ff8080", font=("Consolas", 10),
                          wrap="word", insertbackground="#fff")
            txt.pack(fill="both", expand=True, padx=8, pady=8)
            txt.insert("1.0", f"Произошла ошибка:\n\n{tb}\n\nЛог: {ERROR_LOG}")
            txt.configure(state="disabled")
            r.mainloop()
        except Exception:
            print(tb)


if __name__ == "__main__":
    main()