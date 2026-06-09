"""数据库操作：建表、物品 CRUD、附加项 CRUD。"""
from __future__ import annotations
import sqlite3
from guiwu.config import DB_PATH
from guiwu.models import Item, AdditionalEntry


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            image_type  TEXT    NOT NULL DEFAULT 'default',
            price       REAL    NOT NULL,
            buy_date    TEXT    NOT NULL,
            retire_date TEXT    DEFAULT '',
            notes       TEXT    DEFAULT '',
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS additional_entries (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id     INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            type        TEXT    NOT NULL CHECK(type IN ('收入','支出')),
            amount      REAL    NOT NULL,
            date        TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()


def add_item(item: Item) -> int:
    conn = _connect()
    cur = conn.execute(
        "INSERT INTO items (name, image_type, price, buy_date, retire_date, notes) VALUES (?,?,?,?,?,?)",
        (item.name, item.image_type, item.price, item.buy_date, item.retire_date, item.notes),
    )
    item_id = cur.lastrowid
    for e in item.additional_entries:
        conn.execute(
            "INSERT INTO additional_entries (item_id, name, type, amount, date) VALUES (?,?,?,?,?)",
            (item_id, e.name, e.type, e.amount, e.date),
        )
    conn.commit()
    conn.close()
    return item_id


def update_item(item: Item):
    conn = _connect()
    conn.execute(
        "UPDATE items SET name=?, image_type=?, price=?, buy_date=?, retire_date=?, notes=? WHERE id=?",
        (item.name, item.image_type, item.price, item.buy_date, item.retire_date, item.notes, item.id),
    )
    conn.execute("DELETE FROM additional_entries WHERE item_id=?", (item.id,))
    for e in item.additional_entries:
        conn.execute(
            "INSERT INTO additional_entries (item_id, name, type, amount, date) VALUES (?,?,?,?,?)",
            (item.id, e.name, e.type, e.amount, e.date),
        )
    conn.commit()
    conn.close()


def delete_item(item_id: int):
    conn = _connect()
    conn.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def get_all_items() -> list[Item]:
    conn = _connect()
    item_rows = conn.execute("SELECT * FROM items ORDER BY created_at DESC").fetchall()
    items = []
    for row in item_rows:
        entry_rows = conn.execute(
            "SELECT * FROM additional_entries WHERE item_id=? ORDER BY id ASC", (row["id"],)
        ).fetchall()
        entries = [_row_to_entry(r) for r in entry_rows]
        items.append(_row_to_item(row, entries))
    conn.close()
    return items


def get_item(item_id: int) -> Item | None:
    conn = _connect()
    row = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
    if not row:
        conn.close()
        return None
    entry_rows = conn.execute(
        "SELECT * FROM additional_entries WHERE item_id=? ORDER BY id ASC", (item_id,)
    ).fetchall()
    entries = [_row_to_entry(r) for r in entry_rows]
    conn.close()
    return _row_to_item(row, entries)


def _row_to_item(row: sqlite3.Row, entries: list[AdditionalEntry]) -> Item:
    return Item(
        id=row["id"],
        name=row["name"],
        image_type=row["image_type"],
        price=row["price"],
        buy_date=row["buy_date"],
        retire_date=row["retire_date"],
        notes=row["notes"],
        created_at=row["created_at"],
        additional_entries=entries,
    )


def _row_to_entry(row: sqlite3.Row) -> AdditionalEntry:
    return AdditionalEntry(
        id=row["id"],
        item_id=row["item_id"],
        name=row["name"],
        type=row["type"],
        amount=row["amount"],
        date=row["date"],
        created_at=row["created_at"],
    )
