ESC = 16777216
TAB = 16777217
BACKSPACE = 16777219
RETURN = 16777220
LITTLE_RETURN = 16777221
INSERT = 16777222
DELETE = 16777223
PAUSE = 16777224
HOME = 16777232
END = 16777233
LEFT = 16777234
UP = 16777235
RIGHT = 16777236
DOWN = 16777237
SHIFT = 16777248
CTRL = 16777249
WIN = 16777250
ALT = 16777251
CAPSLOCK = 16777252
NUMSLOCK = 16777253
SCROLLLOCK = 16777254
F1 = 16777264
F2 = 16777265
F3 = 16777266
F4 = 16777267
F5 = 16777268
F6 = 16777269
F7 = 16777270
F8 = 16777271
F9 = 16777272
F10 = 16777273
F11 = 16777274
F12 = 16777275
RIGHT_ARROW = 16777301

# MAXIMUM_STAR = 5e3

# MAIN_COLOR = "#000000"
MAIN_COLOR = "#ffffff"
# MAIN_CAPTION_COLOR = "#222222"
MAIN_CAPTION_COLOR = "#eeeeee"#"#00ff00"
# MAIN_BACKGROUND_COLOR = "#222222"
MAIN_BACKGROUND_COLOR = "#dddddd"#"#ff0000"

BUTTON_BACKGROUND_COLOR = "#336dab"
BUTTON_FOREGROUND_COLOR = "#ffffff"
BUTTON_LIGHT_COLOR = "#eeeeee"

MAIN_TEXT_COLOR = "#ffffff"
MAIN_TEXT_COLOR = "#000000"
MAIN_LTEXT_COLOR = "#666666"
MAIN_L2TEXT_COLOR = "#bbbbbb"

RADIUS = 5

CHUNK = 30 # 窗口更新速度(ms) 值越小窗口动画越流畅, 相应的资源占用更多 (默认为 10 [fps:100], 建议为 30 [fps:33.3])
MAX_CHUNK = 1000 # 窗口前台最长更新间隔(ms), 这用于动态刷新率 (由于 CHUNK_PERCENT 参数存在, 实际间隔可能更长)
CHUNK_PERCENT = 2 # 动态刷新率的增长速度, 这应当是一个大于1的数
SENSITIVITY = 8 # 设置窗口缩放灵敏度 值越大越灵敏 (建议为 5~10)
CLOSE_ANIMATION = -1
