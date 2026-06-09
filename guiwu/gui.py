"""主窗口 GUI：统计栏、筛选排序栏、卡片列表。"""
from __future__ import annotations
import json
import customtkinter as ctk
from datetime import date

from guiwu.config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, ASSETS_DIR, APP_ICON, PROJECT_ROOT, BG_COLOR
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
        self.minsize(600, 400)
        self.configure(fg_color=BG_COLOR)
        self.iconbitmap(str(ASSETS_DIR / APP_ICON))

        self._state_path = PROJECT_ROOT / ".window_state.json"
        self._state = self._load_state()

        # 恢复上次窗口位置/大小
        if "geometry" in self._state:
            self.geometry(self._state["geometry"])
        else:
            self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Header — stats card goes below controls
        self._stats_bar = StatsBar(self)

        # Controls
        self._ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._ctrl_frame.pack(fill="x", padx=20, pady=(20, 12))

        ctrl_font = ctk.CTkFont(size=14)

        self._filter_var = ctk.StringVar(value=self._state.get("filter", FILTER_OPTS[0]))
        ctk.CTkOptionMenu(
            self._ctrl_frame, variable=self._filter_var, values=FILTER_OPTS,
            width=100, font=ctrl_font, height=34, corner_radius=17,
            command=lambda _: self._refresh(),
        ).pack(side="left", padx=(0, 10))

        self._sort_var = ctk.StringVar(value=self._state.get("sort", "购买时间"))
        ctk.CTkOptionMenu(
            self._ctrl_frame, variable=self._sort_var, values=list(SORT_KEYS.keys()),
            width=120, font=ctrl_font, height=34, corner_radius=17,
            command=lambda _: self._refresh(),
        ).pack(side="left", padx=(0, 10))

        self._asc_var = ctk.BooleanVar(value=self._state.get("ascending", True))
        self._asc_btn = ctk.CTkButton(
            self._ctrl_frame, text="↑ 升序" if self._asc_var.get() else "↓ 降序",
            width=80, height=34,
            corner_radius=17, font=ctrl_font,
            command=self._toggle_order,
        )
        self._asc_btn.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            self._ctrl_frame, text="+ 添加物品", width=120, height=34,
            corner_radius=17, font=ctrl_font,
            command=self._open_add_form,
        ).pack(side="right")

        # Cards
        self._card_list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._card_list.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        self._card_widgets: list[ItemCard] = []
        self._refresh()
        self.update_idletasks()

        # stats card below controls, above cards (pack after refresh to stay at top)
        self._stats_bar.pack(fill="x", padx=20, pady=(0, 10), after=self._ctrl_frame)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- state persist ----------

    def _load_state(self) -> dict:
        try:
            if self._state_path.exists():
                return json.loads(self._state_path.read_text())
        except Exception:
            pass
        return {}

    def _save_state(self):
        try:
            self._state_path.write_text(json.dumps({
                "geometry": self.geometry(),
                "filter": self._filter_var.get(),
                "sort": self._sort_var.get(),
                "ascending": self._asc_var.get(),
            }))
        except Exception:
            pass

    def _on_close(self):
        self._save_state()
        self.destroy()

    # ---------- data ----------

    def _refresh(self):
        items = get_all_items()

        filt = self._filter_var.get()
        if filt == "现役":
            items = [it for it in items if not it.is_retired]
        elif filt == "退役":
            items = [it for it in items if it.is_retired]

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
            card.pack(fill="x", pady=(0, 8))
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
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
