"""数据模型：Item、AdditionalEntry 数据类定义。"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


def _parse_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%d").date()


def _days_between(start: date, end: date) -> int:
    return max((end - start).days, 1)


@dataclass
class AdditionalEntry:
    id: Optional[int] = None
    item_id: Optional[int] = None
    name: str = ""
    type: str = "支出"        # "收入" | "支出"
    amount: float = 0.0
    date: str = ""           # YYYY-MM-DD
    created_at: str = ""


@dataclass
class Item:
    id: Optional[int] = None
    name: str = ""
    image_type: str = "_default"
    price: float = 0.0
    buy_date: str = ""           # YYYY-MM-DD
    retire_date: str = ""        # YYYY-MM-DD or empty
    notes: str = ""
    created_at: str = ""
    additional_entries: list[AdditionalEntry] = field(default_factory=list)

    # 净成本 = 购买价格 - 收入总额 + 支出总额
    @property
    def net_cost(self) -> float:
        total = self.price
        for e in self.additional_entries:
            if e.type == "收入":
                total -= e.amount
            else:
                total += e.amount
        return total

    # 使用天数
    @property
    def days_used(self) -> int:
        buy = _parse_date(self.buy_date)
        if not buy:
            return 1
        end = _parse_date(self.retire_date) or date.today()
        return _days_between(buy, end)

    # 日均成本
    @property
    def daily_cost(self) -> float:
        return self.net_cost / self.days_used

    @property
    def is_retired(self) -> bool:
        return bool(self.retire_date)
