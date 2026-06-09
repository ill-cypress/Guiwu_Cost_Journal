"""顶部统计卡片组件：蓝色长方形，上排总数，下排左总资产右日均成本。"""
import customtkinter as ctk
from guiwu.models import Item
from guiwu.config import CARD_BLUE


class StatsBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=16, border_width=0)

        self._total_label = None
        self._asset_value_label = None
        self._daily_value_label = None

    def refresh(self, items: list[Item]):
        total = len(items)
        total_asset = sum(it.price for it in items if not it.is_retired)
        total_daily = sum(it.daily_cost for it in items)

        if self._total_label is None:
            self._build()
        self._total_label.configure(text=f"共 {total} 件物品")
        self._asset_value_label.configure(text=f"¥{total_asset:,.2f}")
        self._daily_value_label.configure(text=f"¥{total_daily:,.2f}/天")

    def _build(self):
        self.configure(fg_color=CARD_BLUE)

        # 上排 — 总数
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=36, pady=(24, 16))
        self._total_label = ctk.CTkLabel(
            top, text="",
            font=ctk.CTkFont(family="Microsoft YaHei", size=20, weight="bold"),
            text_color="white",
        )
        self._total_label.pack(anchor="center")

        # 横分隔线 — 半透明白色
        sep_top = ctk.CTkFrame(self, fg_color="#C8D2E4", height=2)
        sep_top.pack(fill="x", padx=20)

        # 下排 — 左右各两行
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=36, pady=(20, 26))

        left = ctk.CTkFrame(bottom, fg_color="transparent")
        left.pack(side="left", expand=True)
        ctk.CTkLabel(
            left, text="总资产",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14),
            text_color="white",
        ).pack(anchor="center")
        self._asset_value_label = ctk.CTkLabel(
            left, text="",
            font=ctk.CTkFont(family="Microsoft YaHei", size=22, weight="bold"),
            text_color="white",
        )
        self._asset_value_label.pack(anchor="center")

        # 竖分隔线 — 半透明白色
        sep_v = ctk.CTkFrame(bottom, fg_color="#90A5C8", width=2, height=50)
        sep_v.pack(side="left", padx=20)

        right = ctk.CTkFrame(bottom, fg_color="transparent")
        right.pack(side="right", expand=True)
        ctk.CTkLabel(
            right, text="日均成本",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14),
            text_color="white",
        ).pack(anchor="center")
        self._daily_value_label = ctk.CTkLabel(
            right, text="",
            font=ctk.CTkFont(family="Microsoft YaHei", size=22, weight="bold"),
            text_color="white",
        )
        self._daily_value_label.pack(anchor="center")
