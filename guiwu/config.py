"""常量配置：数据库路径、图标枚举列表、窗口默认设置等。"""
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = _PROJECT_ROOT / "guiwu.db"
ICONS_DIR = Path(__file__).parent / "assets" / "icons"
DEFAULT_ICON = "_default"

IMAGE_TYPES = [
    "主机", "显示器", "NAS", "硬盘", "显卡",
    "手机", "平板", "Kindle",
    "笔记本电脑", "电脑", "Mac主机",
    "内存", "CPU", "主板",
    "键盘", "鼠标", "机械臂",
    "风扇", "电源", "充电器", "数据线", "拓展坞",
    "路由器",
    "蓝牙耳机", "有线耳机", "头戴耳机",
    "U盘", "麦克风", "摄像头",
    "音响", "投影仪",
    "游戏机", "手柄", "Switch", "PS5", "Xbox",
    "游戏卡带", "游戏方向盘",
    "VR眼镜", "智能手表",
    "手写笔", "手绘板", "录音笔",
    "无人机", "打印机",
    "移动电源", "GoPro", "Pocket",
    "相机", "镜头", "三脚架", "闪光灯",
    "手环", "手机壳", "鼠标垫", "MP3",
]

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_TITLE = "归物本"
