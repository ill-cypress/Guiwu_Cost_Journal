"""单张物品卡片组件：横条布局，点击触发编辑回调。"""
import customtkinter as ctk
from PIL import Image

from guiwu.config import ICONS_DIR, DEFAULT_ICON, ICON_MAP
from guiwu.models import Item


class ItemCard(ctk.CTkFrame):
    def __init__(self, master, item: Item, on_click, icon_size=52):
        super().__init__(master, corner_radius=14, border_width=0)

        self.item = item
        self._icon_ref = None

        card_fg = "#637A5C" if item.is_retired else "#468C38"
        text_clr = "#E0E0D8" if item.is_retired else "white"
        self.configure(fg_color=card_fg)

        # 左侧图标
        icon_path = self._resolve_icon(item.image_type)
        try:
            pil_img = Image.open(icon_path).resize((icon_size, icon_size))
            self._icon_ref = ctk.CTkImage(pil_img, size=(icon_size, icon_size))
            icon_lbl = ctk.CTkLabel(self, image=self._icon_ref, text="")
            icon_lbl.pack(side="left", padx=(16, 14), pady=14)
        except Exception:
            pass

        # 中间文字区域
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(side="left", fill="both", expand=True, padx=8, pady=13)

        ctk.CTkLabel(
            body, text=item.name, font=ctk.CTkFont(size=18, weight="bold"),
            text_color=text_clr, anchor="w",
        ).pack(anchor="w")

        if item.is_retired:
            detail = (
                f"使用 {item.days_used} 天 · "
                f"买入 ¥{item.price:,.2f} · "
                f"净成本 ¥{item.net_cost:,.2f} · "
                f"日均 ¥{item.daily_cost:,.2f}/天"
            )
        else:
            detail = (
                f"已用 {item.days_used} 天 · "
                f"¥{item.price:,.2f} · "
                f"日均 ¥{item.daily_cost:,.2f}/天"
            )
        ctk.CTkLabel(
            body, text=detail, font=ctk.CTkFont(size=14),
            text_color=text_clr, anchor="w",
        ).pack(anchor="w")

        # 右侧日均成本
        ctk.CTkLabel(
            self, text=f"日均 ¥{item.daily_cost:,.2f}/天",
            font=ctk.CTkFont(size=13), text_color=text_clr,
        ).pack(side="right", padx=16)

        # 点击整张卡片 → 编辑
        self.bind("<Button-1>", lambda e: on_click(item))
        self._bind_children(self, lambda c: c.bind("<Button-1>", lambda e: on_click(item)))

    @staticmethod
    def _bind_children(parent, binder):
        for child in parent.winfo_children():
            binder(child)
            ItemCard._bind_children(child, binder)

    @staticmethod
    def _resolve_icon(image_type: str) -> str:
        filename = ICON_MAP.get(image_type, DEFAULT_ICON)
        path = ICONS_DIR / f"{filename}.png"
        if path.exists():
            return str(path)
        default = ICONS_DIR / f"{DEFAULT_ICON}.png"
        return str(default)
