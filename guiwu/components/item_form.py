"""物品表单窗口：新建/编辑物品信息及附加项列表。"""
from __future__ import annotations
import customtkinter as ctk
from guiwu.config import IMAGE_TYPES, ICONS_DIR, DEFAULT_ICON
from guiwu.models import Item, AdditionalEntry


def _available_image_types() -> list[str]:
    """返回 icons 目录下实际存在的图标文件名（不含扩展名），找不到就用默认列表。"""
    if ICONS_DIR.exists():
        names = sorted(
            p.stem for p in ICONS_DIR.glob("*.png")
            if p.stem != DEFAULT_ICON
        )
        if names:
            names.insert(0, DEFAULT_ICON)
            return names
    return [DEFAULT_ICON] + IMAGE_TYPES


class ItemForm(ctk.CTkToplevel):
    """新建/编辑物品弹窗。自动判断模式：传入 item 为编辑，否则为新建。"""

    def __init__(self, master, item: Item | None, on_save, on_delete=None):
        super().__init__(master)
        self._item = item or Item()
        self._is_edit = item is not None
        self._on_save = on_save
        self._on_delete = on_delete
        self._entry_rows: list[dict] = []   # 附加项 UI 行引用

        self.title("编辑物品" if self._is_edit else "添加物品")
        self.geometry("520x580")
        self.resizable(False, False)
        self.grab_set()

        self._build()

    # ---------- UI ----------

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(20, 0))

        # 名称
        ctk.CTkLabel(scroll, text="名称 *", anchor="w").pack(fill="x")
        self._name = ctk.CTkEntry(scroll)
        self._name.insert(0, self._item.name)
        self._name.pack(fill="x", pady=(2, 12))

        # 图标
        ctk.CTkLabel(scroll, text="图标", anchor="w").pack(fill="x")
        types = _available_image_types()
        self._image_var = ctk.StringVar(value=self._item.image_type)
        self._image_menu = ctk.CTkOptionMenu(scroll, variable=self._image_var, values=types)
        self._image_menu.pack(anchor="w", pady=(2, 12))

        # 价格
        ctk.CTkLabel(scroll, text="价格 *", anchor="w").pack(fill="x")
        self._price = ctk.CTkEntry(scroll)
        if self._item.price:
            self._price.insert(0, f"{self._item.price:.2f}")
        self._price.pack(fill="x", pady=(2, 12))

        # 购买日期
        ctk.CTkLabel(scroll, text="购买日期 * (YYYY-MM-DD)", anchor="w").pack(fill="x")
        self._buy_date = ctk.CTkEntry(scroll)
        self._buy_date.insert(0, self._item.buy_date)
        self._buy_date.pack(fill="x", pady=(2, 12))

        # 退役日期
        ctk.CTkLabel(scroll, text="退役日期 (留空=现役)", anchor="w").pack(fill="x")
        self._retire_date = ctk.CTkEntry(scroll)
        self._retire_date.insert(0, self._item.retire_date)
        self._retire_date.pack(fill="x", pady=(2, 12))

        # 备注
        ctk.CTkLabel(scroll, text="备注", anchor="w").pack(fill="x")
        self._notes = ctk.CTkEntry(scroll)
        self._notes.insert(0, self._item.notes)
        self._notes.pack(fill="x", pady=(2, 12))

        # 附加项
        ctk.CTkLabel(scroll, text="附加项", anchor="w", font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=(8, 4))
        self._entries_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self._entries_frame.pack(fill="x")

        for e in self._item.additional_entries:
            self._add_entry_row(e)

        # 「+ 添加附加项」
        ctk.CTkButton(
            scroll, text="+ 添加附加项", width=140, height=28,
            fg_color="transparent", text_color="#1F6EF5", border_width=1,
            border_color="#1F6EF5", corner_radius=6,
            command=self._add_entry_row,
        ).pack(pady=(8, 12), anchor="w")

        # 底部按钮
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(8, 16))

        if self._is_edit:
            ctk.CTkButton(
                btn_frame, text="删除", fg_color="#D32F2F", hover_color="#B71C1C",
                width=100, height=34, corner_radius=8,
                command=self._handle_delete,
            ).pack(side="left")

        ctk.CTkButton(
            btn_frame, text="保存", fg_color="#2E7D32", hover_color="#1B5E20",
            width=100, height=34, corner_radius=8,
            command=self._handle_save,
        ).pack(side="right")

    # ---------- 附加项行 ----------

    def _add_entry_row(self, entry: AdditionalEntry | None = None):
        entry = entry or AdditionalEntry()
        row_frame = ctk.CTkFrame(self._entries_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)

        # 名称
        name = ctk.CTkEntry(row_frame, width=110, placeholder_text="名称")
        name.insert(0, entry.name)
        name.pack(side="left", padx=(0, 4))

        # 类型
        type_var = ctk.StringVar(value=entry.type)
        type_menu = ctk.CTkOptionMenu(row_frame, variable=type_var, values=["支出", "收入"], width=72)
        type_menu.pack(side="left", padx=(0, 4))

        # 金额
        amt = ctk.CTkEntry(row_frame, width=80, placeholder_text="金额")
        if entry.amount:
            amt.insert(0, f"{entry.amount:.2f}")
        amt.pack(side="left", padx=(0, 4))

        # 日期
        d = ctk.CTkEntry(row_frame, width=100, placeholder_text="YYYY-MM-DD")
        d.insert(0, entry.date)
        d.pack(side="left", padx=(0, 4))

        # 删除按钮
        del_btn = ctk.CTkButton(
            row_frame, text="✕", width=28, height=28,
            fg_color="transparent", text_color="#999",
            hover_color="#FEE", corner_radius=6,
            command=lambda: self._remove_entry_row(row_frame),
        )
        del_btn.pack(side="left")

        self._entry_rows.append({
            "frame": row_frame, "name": name, "type": type_var,
            "amount": amt, "date": d,
        })

    def _remove_entry_row(self, frame):
        for i, r in enumerate(self._entry_rows):
            if r["frame"] is frame:
                r["frame"].destroy()
                self._entry_rows.pop(i)
                break

    # ---------- 保存 / 删除 ----------

    def _collect(self) -> Item:
        image_type = self._image_var.get() or DEFAULT_ICON
        price = float(self._price.get() or 0)
        buy_date = self._buy_date.get().strip()
        retire_date = self._retire_date.get().strip()

        entries = []
        for r in self._entry_rows:
            e_name = r["name"].get().strip()
            if not e_name:
                continue
            e_type = r["type"].get()
            e_amount = float(r["amount"].get() or 0)
            e_date = r["date"].get().strip()
            entries.append(AdditionalEntry(
                name=e_name, type=e_type, amount=e_amount, date=e_date,
            ))

        return Item(
            id=self._item.id,
            name=self._name.get().strip(),
            image_type=image_type,
            price=price,
            buy_date=buy_date,
            retire_date=retire_date,
            notes=self._notes.get().strip(),
            additional_entries=entries,
        )

    def _handle_save(self):
        item = self._collect()
        if not item.name or not item.buy_date:
            return          # 静默忽略（可加校验提示）
        self._on_save(item)
        self.destroy()

    def _handle_delete(self):
        if self._on_delete:
            self._on_delete(self._item)
        self.destroy()
