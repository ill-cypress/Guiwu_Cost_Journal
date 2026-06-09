"""顶部统计栏组件：物品总数、总资产、日均总成本。"""
import customtkinter as ctk
from guiwu.models import Item


class StatsBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.labels: list[ctk.CTkLabel] = []

    def refresh(self, items: list[Item]):
        for lbl in self.labels:
            lbl.destroy()
        self.labels.clear()

        total = len(items)
        active = sum(1 for it in items if not it.is_retired)
        total_asset = sum(it.price for it in items if not it.is_retired)
        total_daily = sum(it.daily_cost for it in items)

        texts = [
            f"共 {total} 件",
            f"现役 {active} 件",
            f"总资产 ¥{total_asset:,.2f}",
            f"日均总成本 ¥{total_daily:,.2f}/天",
        ]
        for t in texts:
            lbl = ctk.CTkLabel(self, text=t, font=ctk.CTkFont(size=16))
            lbl.pack(side="left", padx=(0, 20))
            self.labels.append(lbl)

        self.pack(fill="x", padx=16, pady=(16, 8))
