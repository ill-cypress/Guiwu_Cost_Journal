"""主窗口 GUI：统计栏、筛选排序栏、卡片列表。"""
from __future__ import annotations
import customtkinter as ctk
from datetime import date

from guiwu.config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
from guiwu.database import get_all_items, delete_item as db_delete
from guiwu.models import Item
from guiwu.components.stats_bar import StatsBar
from guiwu.components.item_card import ItemCard
from guiwu.components.item_form import ItemForm


SORT_KEYS = {
    "购买时间": lambda it: it.buy_date,
    "购买价格": lambda it: it.price,
    "使用天数": lambda it: it.days_used,
    "日均成本": lambda it: it.daily_cost,
}

FILTER_OPTS = ["全部", "现役", "退役"]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(600, 400)

        # Header
        self._stats_bar = StatsBar(self)

        # Controls
        self._ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._ctrl_frame.pack(fill="x", padx=16, pady=(4, 8))

        self._filter_var = ctk.StringVar(value=FILTER_OPTS[0])
        ctk.CTkOptionMenu(
            self._ctrl_frame, variable=self._filter_var, values=FILTER_OPTS,
            width=100, command=lambda _: self._refresh(),
        ).pack(side="left", padx=(0, 6))

        self._sort_var = ctk.StringVar(value="购买时间")
        ctk.CTkOptionMenu(
            self._ctrl_frame, variable=self._sort_var, values=list(SORT_KEYS.keys()),
            width=120, command=lambda _: self._refresh(),
        ).pack(side="left", padx=(0, 6))

        self._asc_var = ctk.BooleanVar(value=True)
        self._asc_btn = ctk.CTkButton(
            self._ctrl_frame, text="↑ 升序", width=70, height=28,
            corner_radius=6, command=self._toggle_order,
        )
        self._asc_btn.pack(side="left")

        ctk.CTkButton(
            self._ctrl_frame, text="+ 添加物品", width=100, height=28,
            corner_radius=6, command=self._open_add_form,
        ).pack(side="right")

        # Cards
        self._card_list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._card_list.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self._card_widgets: list[ItemCard] = []
        self._refresh()

    # ---------- data ----------

    def _refresh(self):
        items = get_all_items()

        # 筛选
        filt = self._filter_var.get()
        if filt == "现役":
            items = [it for it in items if not it.is_retired]
        elif filt == "退役":
            items = [it for it in items if it.is_retired]

        # 排序
        key_fn = SORT_KEYS[self._sort_var.get()]
        ascending = self._asc_var.get()
        items.sort(key=key_fn, reverse=not ascending)

        self._stats_bar.refresh(items)
        self._rebuild_cards(items)

    def _rebuild_cards(self, items: list[Item]):
        for c in self._card_widgets:
            c.destroy()
        self._card_widgets.clear()

        for item in items:
            card = ItemCard(self._card_list, item, on_click=self._open_edit_form)
            card.pack(fill="x", pady=3)
            self._card_widgets.append(card)

    def _toggle_order(self):
        self._asc_var.set(not self._asc_var.get())
        self._asc_btn.configure(text="↑ 升序" if self._asc_var.get() else "↓ 降序")
        self._refresh()

    # ---------- forms ----------

    def _open_add_form(self):
        ItemForm(self, None, on_save=self._on_form_save)

    def _open_edit_form(self, item: Item):
        ItemForm(self, item, on_save=self._on_form_save, on_delete=self._on_form_delete)

    def _on_form_save(self, item: Item):
        from guiwu.database import add_item, update_item
        if item.id is None:
            add_item(item)
        else:
            update_item(item)
        self._refresh()

    def _on_form_delete(self, item: Item):
        db_delete(item.id)
        self._refresh()


def launch():
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
