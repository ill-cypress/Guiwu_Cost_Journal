"""物品表单窗口：新建/编辑物品信息及附加项列表。"""
from __future__ import annotations
import customtkinter as ctk
from datetime import date as date_cls
from PIL import Image

from guiwu.config import IMAGE_TYPES, ICONS_DIR, DEFAULT_ICON, ICON_MAP, BG_COLOR
from guiwu.models import Item, AdditionalEntry
from guiwu.components.date_picker import DatePicker


def _available_image_types() -> list[str]:
    """返回有对应图标文件的分类名列表。"""
    types = []
    for t in IMAGE_TYPES:
        filename = ICON_MAP.get(t, "")
        if filename and (ICONS_DIR / f"{filename}.png").exists():
            types.append(t)
    return ["默认图标"] + types if types else ["默认图标"] + IMAGE_TYPES


def _icon_filename(image_type: str) -> str:
    if image_type == "默认图标":
        return DEFAULT_ICON
    return ICON_MAP.get(image_type, DEFAULT_ICON)


class ItemForm(ctk.CTkToplevel):
    def __init__(self, master, item: Item | None, on_save, on_delete=None):
        super().__init__(master)
        self._item = item or Item()
        self._is_edit = item is not None
        self._on_save = on_save
        self._on_delete = on_delete
        self._entry_rows: list[dict] = []

        self.title("编辑物品" if self._is_edit else "添加物品")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=BG_COLOR)

        self.update_idletasks()
        mw = master.winfo_toplevel()
        fx = mw.winfo_rootx() + (mw.winfo_width() - 560) // 2
        fy = mw.winfo_rooty() + (mw.winfo_height() - 640) // 2
        self.geometry(f"560x640+{fx}+{fy}")

        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(20, 0))

        # 名称
        ctk.CTkLabel(scroll, text="名称 *", anchor="w", font=ctk.CTkFont(size=15)).pack(fill="x")
        self._name_var = ctk.StringVar(value=self._item.name)
        self._name_var.trace_add("write", lambda *_: self._update_save_button())
        self._name = ctk.CTkEntry(scroll, textvariable=self._name_var, font=ctk.CTkFont(size=15), height=36, corner_radius=18, fg_color="#EEE5C8")
        self._name.pack(fill="x", pady=(2, 14))

        # 图标
        ctk.CTkLabel(scroll, text="图标", anchor="w", font=ctk.CTkFont(size=15)).pack(fill="x")
        self._current_image_type = self._item.image_type if self._item.image_type and self._item.image_type not in ("_default", "default") else "默认图标"
        icon_btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        icon_btn_frame.pack(anchor="w", pady=(2, 12))

        self._icon_preview_img = None
        self._icon_preview = ctk.CTkLabel(icon_btn_frame, text="", width=36, height=36)
        self._icon_preview.pack(side="left", padx=(0, 8))
        self._update_icon_preview(self._current_image_type)

        self._icon_label = ctk.CTkLabel(icon_btn_frame, text=self._current_image_type, font=ctk.CTkFont(size=15))
        self._icon_label.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            icon_btn_frame, text="选择图标", width=96, height=34,
            corner_radius=17, font=ctk.CTkFont(size=14),
            command=self._open_icon_picker,
        ).pack(side="left")

        # 价格
        ctk.CTkLabel(scroll, text="价格 *", anchor="w", font=ctk.CTkFont(size=15)).pack(fill="x")
        self._price_var = ctk.StringVar()
        if self._item.price:
            self._price_var.set(f"{self._item.price:.2f}")
        self._price_var.trace_add("write", lambda *_: self._update_save_button())
        self._price_var.trace_add("write", self._make_decimal_filter(self._price_var))
        self._price = ctk.CTkEntry(scroll, textvariable=self._price_var, font=ctk.CTkFont(size=15), height=36, corner_radius=18, fg_color="#EEE5C8")
        self._price.pack(fill="x", pady=(2, 12))

        # 购买日期
        ctk.CTkLabel(scroll, text="购买日期 *", anchor="w", font=ctk.CTkFont(size=15)).pack(fill="x")
        self._buy_date_picker = DatePicker(scroll, command=self._on_form_field_changed)
        self._buy_date_picker.set_date(self._item.buy_date or date_cls.today().isoformat())
        self._buy_date_picker.pack(fill="x", pady=(2, 12))

        # 退役日期
        self._retired_var = ctk.BooleanVar(value=self._item.is_retired)
        self._retired_cb = ctk.CTkCheckBox(
            scroll, text="已退役", variable=self._retired_var,
            font=ctk.CTkFont(size=15),
            command=self._toggle_retire_picker,
        )
        self._retired_cb.pack(anchor="w", pady=(2, 4))

        self._retire_date_label = ctk.CTkLabel(scroll, text="退役日期", anchor="w", font=ctk.CTkFont(size=15))
        self._retire_date_picker = DatePicker(scroll)
        self._retire_date_picker.set_date(self._item.retire_date or date_cls.today().isoformat())
        self._retire_date_picker.pack(fill="x", pady=(2, 12))
        if not self._item.is_retired:
            self._retire_date_label.pack_forget()
            self._retire_date_picker.pack_forget()

        # 备注
        ctk.CTkLabel(scroll, text="备注", anchor="w", font=ctk.CTkFont(size=15)).pack(fill="x")
        self._notes = ctk.CTkEntry(scroll, font=ctk.CTkFont(size=15), height=36, corner_radius=18, fg_color="#EEE5C8")
        self._notes.insert(0, self._item.notes)
        self._notes.pack(fill="x", pady=(2, 12))

        # 附加项
        ctk.CTkLabel(scroll, text="附加项", anchor="w", font=ctk.CTkFont(size=15, weight="bold")).pack(fill="x", pady=(8, 4))
        self._entries_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self._entries_frame.pack(fill="x")

        # "添加附加项" 按钮 — 放在 entries_frame 内，新行插入到按钮之前
        self._add_entry_btn = ctk.CTkButton(
            self._entries_frame, text="+ 添加附加项", width=150, height=34,
            fg_color="#1F6EF5", text_color="white",
            corner_radius=17, font=ctk.CTkFont(size=14),
            command=self._add_entry_row,
        )
        self._add_entry_btn.pack(pady=(8, 0), anchor="w")

        for e in self._item.additional_entries:
            self._add_entry_row(e)

        # 底部按钮
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(8, 16))

        if self._is_edit:
            ctk.CTkButton(
                btn_frame, text="删除", fg_color="#D32F2F", hover_color="#B71C1C",
                width=110, height=38, corner_radius=19, font=ctk.CTkFont(size=15),
                command=self._handle_delete,
            ).pack(side="left")

        self._save_btn = ctk.CTkButton(
            btn_frame, text="保存", width=110, height=38,
            corner_radius=19, font=ctk.CTkFont(size=15),
            command=self._handle_save,
        )
        self._save_btn.pack(side="right")
        self._update_save_button()

    def _toggle_retire_picker(self):
        if self._retired_var.get():
            self._retire_date_label.pack(after=self._retired_cb, anchor="w", pady=(8, 2))
            self._retire_date_picker.pack(after=self._retire_date_label, fill="x", pady=(2, 12))
        else:
            self._retire_date_label.pack_forget()
            self._retire_date_picker.pack_forget()

    def _add_entry_row(self, entry: AdditionalEntry | None = None):
        entry = entry or AdditionalEntry()
        row_frame = ctk.CTkFrame(self._entries_frame, fg_color="transparent")
        row_frame.pack(before=self._add_entry_btn, fill="x", pady=2)

        name_var = ctk.StringVar(value=entry.name)
        name_var.trace_add("write", lambda *_: self._update_save_button())
        name = ctk.CTkEntry(row_frame, textvariable=name_var, width=110, placeholder_text="名称", font=ctk.CTkFont(size=14), height=34, corner_radius=17, fg_color="#EEE5C8")
        name.pack(side="left", padx=(0, 4))

        type_var = ctk.StringVar(value=entry.type)
        ctk.CTkOptionMenu(row_frame, variable=type_var, values=["支出", "收入"], width=72, font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 4))

        amt_var = ctk.StringVar()
        if entry.amount:
            amt_var.set(f"{entry.amount:.2f}")
        amt_var.trace_add("write", self._make_decimal_filter(amt_var))
        amt = ctk.CTkEntry(row_frame, textvariable=amt_var, width=80, placeholder_text="金额", font=ctk.CTkFont(size=14), height=34, corner_radius=17, fg_color="#EEE5C8")
        amt.pack(side="left", padx=(0, 4))

        dp = DatePicker(row_frame)
        dp.set_date(entry.date or date_cls.today().isoformat())
        dp.pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            row_frame, text="✕", width=32, height=32,
            fg_color="transparent", text_color="#999",
            hover_color="#FEE", corner_radius=16, font=ctk.CTkFont(size=15),
            command=lambda: self._remove_entry_row(row_frame),
        ).pack(side="left")

        self._entry_rows.append({
            "frame": row_frame, "name": name, "type": type_var,
            "amount": amt, "date": dp,
        })
        if hasattr(self, "_save_btn"):
            self._update_save_button()

    def _remove_entry_row(self, frame):
        for i, r in enumerate(self._entry_rows):
            if r["frame"] is frame:
                r["frame"].destroy()
                self._entry_rows.pop(i)
                break
        self._update_save_button()

    def _on_form_field_changed(self, *_):
        self._update_save_button()

    def _update_save_button(self):
        if self._validate():
            self._save_btn.configure(fg_color="#2E7D32", hover_color="#1B5E20", border_width=0, text_color="white")
        else:
            self._save_btn.configure(fg_color="transparent", hover_color="#E8F5E9", border_width=2, border_color="#2E7D32", text_color="#2E7D32")

    def _update_icon_preview(self, image_type: str):
        filename = _icon_filename(image_type)
        try:
            img = Image.open(ICONS_DIR / f"{filename}.png").resize((36, 36))
            self._icon_preview_img = ctk.CTkImage(img, size=(36, 36))
            self._icon_preview.configure(image=self._icon_preview_img)
        except Exception:
            self._icon_preview.configure(image=None)

    def _open_icon_picker(self):
        popup = ctk.CTkToplevel(self)
        popup.title("选择图标")
        popup.geometry("420x460")
        popup.resizable(False, False)
        popup.grab_set()
        popup.configure(fg_color=BG_COLOR)

        # 居中于父窗口
        popup.update_idletasks()
        pw, ph = popup.winfo_width(), popup.winfo_height()
        fx = self.winfo_rootx() + (self.winfo_width() - pw) // 2
        fy = self.winfo_rooty() + (self.winfo_height() - ph) // 2
        popup.geometry(f"+{fx}+{fy}")

        scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        row_frame = None
        for i, t in enumerate(_available_image_types()):
            if i % 4 == 0:
                row_frame = ctk.CTkFrame(scroll, fg_color="transparent")
                row_frame.pack(fill="x", pady=3)

            filename = _icon_filename(t)
            frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            frame.pack(side="left", expand=True, fill="both", padx=4)

            try:
                img = Image.open(ICONS_DIR / f"{filename}.png").resize((44, 44))
                ctk_img = ctk.CTkImage(img, size=(44, 44))
                img_label = ctk.CTkLabel(frame, image=ctk_img, text="")
                img_label.image = ctk_img
                img_label.pack()
            except Exception:
                pass

            ctk.CTkLabel(frame, text=t, font=ctk.CTkFont(size=13), text_color="#333333", anchor="center").pack()

            img_label.bind("<Button-1>", lambda e, v=t: self._on_icon_selected(v, popup))
            for child in frame.winfo_children():
                child.bind("<Button-1>", lambda e, v=t: self._on_icon_selected(v, popup))
            frame.bind("<Button-1>", lambda e, v=t: self._on_icon_selected(v, popup))

    def _on_icon_selected(self, image_type: str, popup: ctk.CTkToplevel):
        self._current_image_type = image_type
        self._icon_label.configure(text=image_type)
        self._update_icon_preview(image_type)
        popup.destroy()

    def _collect(self) -> Item:
        image_type = self._current_image_type
        if image_type == "默认图标":
            image_type = DEFAULT_ICON
        price = float(self._price_var.get() or 0)
        buy_date = self._buy_date_picker.get().strip()
        retire_date = self._retire_date_picker.get().strip() if self._retired_var.get() else ""

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
            name=self._name_var.get().strip(),
            image_type=image_type,
            price=price,
            buy_date=buy_date,
            retire_date=retire_date,
            notes=self._notes.get().strip(),
            additional_entries=entries,
        )

    def _validate(self):
        name_ok = bool(self._name_var.get().strip())
        price_ok = bool(self._price_var.get().strip())
        buy_date_ok = bool(self._buy_date_picker.get().strip())
        entry_names_ok = all(bool(r["name"].get().strip()) for r in self._entry_rows)
        return name_ok and price_ok and buy_date_ok and entry_names_ok

    def _make_decimal_filter(self, var):
        def _filter(*_):
            val = var.get()
            filtered = []
            has_dot = False
            for c in val:
                if c.isdigit():
                    filtered.append(c)
                elif c == "." and not has_dot:
                    filtered.append(c)
                    has_dot = True
            result = "".join(filtered)
            if result != val:
                var.set(result)
        return _filter

    def _handle_save(self):
        if not self._validate():
            return
        item = self._collect()
        self._on_save(item)
        self.destroy()

    def _handle_delete(self):
        if self._on_delete:
            self._on_delete(self._item)
        self.destroy()
