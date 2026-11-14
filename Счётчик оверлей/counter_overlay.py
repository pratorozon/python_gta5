import tkinter as tk
from pynput import keyboard, mouse


class CounterOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Счётчик")

        # Оверлей: поверх всех окон, без рамки, прозрачный
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.opacity = 0.45
        self.root.attributes("-alpha", self.opacity)
        self.root.configure(bg="black")

        self.root.geometry("+50+50")

        self.count = 0
        self.target_key = None
        self.listening = False

        # --- Верхняя панель для перетаскивания ---
        self.drag_bar = tk.Frame(self.root, bg="gray15", height=22, cursor="fleur")
        self.drag_bar.pack(fill="x")
        self.drag_bar.bind("<Button-1>", self.start_drag)
        self.drag_bar.bind("<B1-Motion>", self.do_drag)

        # --- Отображение счёта ---
        self.label = tk.Label(
            self.root, text="0", font=("Arial", 42, "bold"),
            fg="lime", bg="black", width=5
        )
        self.label.pack(padx=8, pady=2)

        # --- Инфо о назначенной кнопке ---
        self.info = tk.Label(
            self.root, text="Кнопка не назначена",
            font=("Arial", 9), fg="white", bg="black"
        )
        self.info.pack()

        # --- Ручная правка счёта: −1 / +1 ---
        edit_frame = tk.Frame(self.root, bg="black")
        edit_frame.pack(pady=3)

        tk.Button(
            edit_frame, text="−1", command=lambda: self.adjust(-1),
            bg="gray30", fg="white", relief="flat", width=4,
            activebackground="gray50"
        ).pack(side="left", padx=2)

        tk.Button(
            edit_frame, text="+1", command=lambda: self.adjust(+1),
            bg="gray30", fg="white", relief="flat", width=4,
            activebackground="gray50"
        ).pack(side="left", padx=2)

        # --- Основные кнопки управления ---
        btn_frame = tk.Frame(self.root, bg="black")
        btn_frame.pack(pady=3)

        tk.Button(
            btn_frame, text="Назначить", command=self.assign_key,
            bg="gray25", fg="white", relief="flat", width=10
        ).pack(side="left", padx=2)

        tk.Button(
            btn_frame, text="Сброс", command=self.reset,
            bg="darkred", fg="white", relief="flat", width=6
        ).pack(side="left", padx=2)

        tk.Button(
            btn_frame, text="✕", command=self.quit_app,
            bg="black", fg="red", relief="flat", width=2
        ).pack(side="left", padx=2)

        # --- Ползунок прозрачности ---
        alpha_frame = tk.Frame(self.root, bg="black")
        alpha_frame.pack(fill="x", padx=6, pady=(0, 4))

        tk.Label(
            alpha_frame, text="α", fg="white", bg="black", font=("Arial", 9)
        ).pack(side="left")

        self.alpha_scale = tk.Scale(
            alpha_frame, from_=0.15, to=1.0, resolution=0.01,
            orient="horizontal", showvalue=False,
            bg="black", fg="white", highlightthickness=0,
            troughcolor="gray25", sliderlength=12,
            command=self.set_alpha
        )
        self.alpha_scale.set(self.opacity)
        self.alpha_scale.pack(side="left", fill="x", expand=True, padx=4)

        # Слушатели
        self.listener = None
        self.mouse_listener = None

        self.root.mainloop()

    # ---------- Прозрачность ----------
    def set_alpha(self, val):
        self.opacity = float(val)
        self.root.attributes("-alpha", self.opacity)

    # ---------- Перетаскивание ----------
    def start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    # ---------- Назначение кнопки ----------
    def assign_key(self):
        self.info.config(text="Нажми любую кнопку...")
        self.listening = True

        if self.listener:
            self.listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

        def on_press(key):
            if not self.listening:
                return False
            try:
                if hasattr(key, 'char') and key.char:
                    name = key.char
                else:
                    name = str(key).replace("Key.", "")
            except Exception:
                name = str(key)
            self._set_target(name, key)
            return False

        def on_click(x, y, button, pressed):
            if not self.listening or not pressed:
                return
            if self._is_over_overlay(x, y):
                return
            self._set_target(str(button).replace("Button.", "mouse_"), button)
            return False

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()

    def _set_target(self, name, raw):
        self.listening = False
        self.target_key = raw
        self.info.config(text=f"Кнопка: {name}")
        self.start_counting()

    def _is_over_overlay(self, x, y):
        """Игнорировать клики по самому окну оверлея."""
        try:
            wx, wy = self.root.winfo_x(), self.root.winfo_y()
            ww, wh = self.root.winfo_width(), self.root.winfo_height()
            return wx <= x <= wx + ww and wy <= y <= wy + wh
        except Exception:
            return False

    # ---------- Подсчёт ----------
    def start_counting(self):
        if self.listener:
            self.listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

        def on_press(key):
            try:
                if key == self.target_key:
                    self.increment()
            except Exception:
                pass

        def on_click(x, y, button, pressed):
            if not pressed:
                return
            if str(button) == str(self.target_key) and not self._is_over_overlay(x, y):
                self.increment()

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()

    def increment(self):
        self.count += 1
        self.root.after(0, self._refresh_label)

    # ---------- Ручная правка ----------
    def adjust(self, delta):
        self.count = max(0, self.count + delta)  # не уходим в минус
        self._refresh_label()

    def _refresh_label(self):
        self.label.config(text=str(self.count))

    # ---------- Сброс ----------
    def reset(self):
        self.count = 0
        self._refresh_label()

    # ---------- Выход ----------
    def quit_app(self):
        if self.listener:
            self.listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    CounterOverlay()