"""归物本 — 通过 python -m guiwu 启动。"""

from guiwu.database import init_db
from guiwu.gui import launch

def main():
    init_db()
    launch()

if __name__ == "__main__":
    main()
