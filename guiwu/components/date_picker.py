"""CustomTkinter 风格日期选择器：只读输入 + 弹出日历。"""
from __future__ import annotations
import customtkinter as ctk
from datetime import date as date_cls, timedelta
import calendar


class DatePicker(ctk.CTkFrame):
    """只读日期输入框，点击弹出日历。"""

    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._command = command

        self._entry = ctk.CTkEntry(self)
        self._entry.pack(fill="x")
        self._entry.configure(state="readonly")
        self._entry.bind("<Button-1>", self._open_popup)

        self._popup: ctk.CTkToplevel | None = None
        self._current = date_cls.today()
        self._selected = date_cls.today()

    def get(self) -> str:
        return self._entry.get()

    def set_date(self, date_str: str):
        self._entry.configure(state="normal")
        self._entry.delete(0, "end")
        if date_str:
            self._entry.insert(0, date_str)
            try:
                parts = date_str.split("-")
                self._selected = date_cls(int(parts[0]), int(parts[1]), int(parts[2]))
                self._current = self._selected
            except (ValueError, IndexError):
                pass
        self._entry.configure(state="readonly")

    def _open_popup(self, event=None):
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()

        self._popup = ctk.CTkToplevel(self)
        self._popup.title("")
        self._popup.geometry("280x270")
        self._popup.resizable(False, False)
        self._popup.grab_set()
        self._popup.configure(fg_color="white")

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self._popup.geometry(f"+{x}+{y}")

        year = self._current.year
        month = self._current.month

        # 顶部导航
        nav = ctk.CTkFrame(self._popup, fg_color="transparent")
        nav.pack(fill="x", padx=8, pady=(8, 4))

        arrow_font = ctk.CTkFont(size=16, weight="bold")

        ctk.CTkButton(
            nav, text="«", width=28, height=28, font=arrow_font,
            command=lambda: self._change_year(-1),
        ).pack(side="left", padx=(0, 2))

        ctk.CTkButton(
            nav, text="‹", width=28, height=28, font=arrow_font,
            command=lambda: self._change_month(-1),
        ).pack(side="left")

        self._month_label = ctk.CTkLabel(
            nav, text=f"{year}年{month}月",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#222222",
        )
        self._month_label.pack(side="left", expand=True)

        # 先 pack 年按钮 (»)，让它占据最右边
        ctk.CTkButton(
            nav, text="»", width=28, height=28, font=arrow_font,
            command=lambda: self._change_year(1),
        ).pack(side="right")

        # 再 pack 月按钮 (›)，它会自动放在 » 的左边（更靠近标签）
        ctk.CTkButton(
            nav, text="›", width=28, height=28, font=arrow_font,
            command=lambda: self._change_month(1),
        ).pack(side="right", padx=(0, 0))

        # 星期头
        dow_frame = ctk.CTkFrame(self._popup, fg_color="transparent")
        dow_frame.pack(fill="x", padx=8, pady=(4, 2))
        for d in ("一", "二", "三", "四", "五", "六", "日"):
            ctk.CTkLabel(
                dow_frame, text=d, width=32,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#555555",
            ).pack(side="left", expand=True)

        # 日期网格
        self._days_frame = ctk.CTkFrame(self._popup, fg_color="transparent")
        self._days_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        for r in range(6):
            self._days_frame.grid_rowconfigure(r, weight=1)
        for c in range(7):
            self._days_frame.grid_columnconfigure(c, weight=1)

        self._render_days()

    def _change_year(self, delta: int):
        self._current = date_cls(self._current.year + delta, self._current.month, 1)
        self._month_label.configure(text=f"{self._current.year}年{self._current.month}月")
        self._render_days()

    def _change_month(self, delta: int):
        month = self._current.month + delta
        year = self._current.year
        if month < 1:
            year -= 1
            month = 12
        elif month > 12:
            year += 1
            month = 1
        self._current = date_cls(year, month, 1)
        self._month_label.configure(text=f"{year}年{month}月")
        self._render_days()

    def _render_days(self):
        for w in self._days_frame.winfo_children():
            w.destroy()

        year = self._current.year
        month = self._current.month
        today = date_cls.today()

        cal = calendar.monthcalendar(year, month)
        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue
                d = date_cls(year, month, day)
                future = d > today

                is_today = (d == today)
                is_selected = (d == self._selected and d.month == self._selected.month)

                if is_today:
                    fg = "#E3F2FD"
                    tc = "#1565C0"
                elif is_selected:
                    fg = "#1F6EF5"
                    tc = "white"
                else:
                    fg = "transparent"
                    tc = "#444444"

                if future:
                    tc = "#CCCCCC"

                btn = ctk.CTkButton(
                    self._days_frame, text=str(day), width=32, height=28,
                    corner_radius=6,
                    fg_color=fg, text_color=tc,
                    hover_color="#E8E8E8",
                    state="disabled" if future else "normal",
                    command=lambda d=d: self._select_date(d) if d <= today else None,
                )
                btn.grid(row=row_idx, column=col_idx, padx=1, pady=1, sticky="nsew")

    def _select_date(self, d: date_cls):
        date_str = d.isoformat()
        self._entry.configure(state="normal")
        self._entry.delete(0, "end")
        self._entry.insert(0, date_str)
        self._entry.configure(state="readonly")
        self._current = d
        self._selected = d
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
        if self._command:
            self._command(date_str)
