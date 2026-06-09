"""常量配置：数据库路径、图标枚举列表、窗口默认设置等。"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "guiwu.db"
ICONS_DIR = Path(__file__).parent / "assets" / "icons"
ASSETS_DIR = Path(__file__).parent / "assets"
APP_ICON = "guiwu_icon.ico"
DEFAULT_ICON = "default"

IMAGE_TYPES = [
    "主机", "显示器", "硬盘",
    "手机", "平板",
    "笔记本电脑",
    "键盘", "鼠标",
    "充电器", "数据线", "拓展坞",
    "路由器",
    "蓝牙耳机", "头戴耳机",
    "U盘", "麦克风", "摄像头",
    "音响", "投影仪",
    "游戏机", "手柄",
    "智能手表",
    "无人机", "打印机",
    "移动电源",
    "相机", "镜头", "闪光灯",
    "台灯", "电视",
]

# 中文分类 → 英文图标文件名（不含 .png）
ICON_MAP = {
    "主机": "desktop",
    "显示器": "monitor",
    "硬盘": "HDD",
    "手机": "phone",
    "平板": "tablet",
    "笔记本电脑": "laptop",
    "键盘": "keyboard",
    "鼠标": "wireless_mouse",
    "充电器": "charger",
    "数据线": "data_cable",
    "拓展坞": "docking_station",
    "路由器": "router",
    "蓝牙耳机": "bluetooth_earphone",
    "头戴耳机": "over_ear_headphones",
    "U盘": "USB_flash_drive",
    "麦克风": "microphone",
    "摄像头": "webcam",
    "音响": "speaker",
    "投影仪": "projecter",
    "游戏机": "game_console",
    "手柄": "gamepad",
    "智能手表": "watch",
    "无人机": "drone",
    "打印机": "printer",
    "移动电源": "power_bank",
    "相机": "camera",
    "镜头": "camera_lens",
    "闪光灯": "flash",
    "台灯": "lamp",
    "电视": "TV",
}

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_TITLE = "归物本"
