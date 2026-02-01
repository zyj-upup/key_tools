import ctypes
import time
import sys

# 定义虚拟键码常量
VK_CONTROL = 0x11  # Ctrl键
VK_SHIFT = 0x10  # Shift键
VK_SUBTRACT = 0x6D  # 小键盘减号键
VK_ESCAPE = 0x1B  # ESC键用于退出程序

# 加载Windows API
user32 = ctypes.WinDLL('user32', use_last_error=True)


def get_key_state(vk_code):
    """获取按键状态（是否按下）"""
    return user32.GetAsyncKeyState(vk_code) & 0x8000 != 0


def keybd_event(bVk, bScan, dwFlags, dwExtraInfo):
    """模拟按键事件"""
    user32.keybd_event(bVk, bScan, dwFlags, dwExtraInfo)


def type_string(text):
    """直接输入字符串（使用SendInput API）"""

    # 定义必要的结构体
    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.c_ushort),
            ("wScan", ctypes.c_ushort),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
        ]

    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", ctypes.c_ulong),
            ("ki", KEYBDINPUT),
            ("padding", ctypes.c_ulong * 2)
        ]

    # 定义常量
    INPUT_KEYBOARD = 1
    KEYEVENTF_UNICODE = 0x0004
    KEYEVENTF_KEYUP = 0x0002

    # 创建输入结构数组
    inputs = (INPUT * (len(text) * 2))()

    # 填充输入结构
    for i, char in enumerate(text):
        # 按键按下
        inputs[i * 2].type = INPUT_KEYBOARD
        inputs[i * 2].ki = KEYBDINPUT(0, ord(char), KEYEVENTF_UNICODE, 0, None)

        # 按键释放
        inputs[i * 2 + 1].type = INPUT_KEYBOARD
        inputs[i * 2 + 1].ki = KEYBDINPUT(0, ord(char), KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, None)

    # 发送输入
    user32.SendInput(len(text) * 2, inputs, ctypes.sizeof(INPUT))


def simulate_string(text):
    """模拟输入字符串"""
    # 释放修饰键（如果需要）
    if get_key_state(VK_CONTROL):
        keybd_event(VK_CONTROL, 0, 0x0002, 0)  # 释放Ctrl

    if get_key_state(VK_SHIFT):
        keybd_event(VK_SHIFT, 0, 0x0002, 0)  # 释放Shift

    # 短暂延迟确保释放生效
    time.sleep(0.05)

    # 直接输入字符串
    type_string(text)


def main():
    print("监控中... 按下 Ctrl+Shift+小键盘减号 将触发文本输入 (按ESC退出)")
    print("注意：此版本不需要管理员权限")

    # 用于避免重复触发的标志
    last_combo_state = False

    try:
        while True:
            # 检查退出键
            if get_key_state(VK_ESCAPE):
                print("检测到ESC键，退出程序")
                break

            # 检查组合键状态
            ctrl_pressed = get_key_state(VK_CONTROL)
            shift_pressed = get_key_state(VK_SHIFT)
            numpad_minus_pressed = get_key_state(VK_SUBTRACT)

            combo_active = ctrl_pressed and shift_pressed and numpad_minus_pressed

            # 如果组合键刚被按下（之前未按下）
            if combo_active and not last_combo_state:
                print("检测到 Ctrl+Shift+小键盘减号 组合键")
                simulate_string("332211")  # 直接输入字符串

            # 更新状态
            last_combo_state = combo_active

            # 降低CPU占用率
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n程序已退出")


if __name__ == "__main__":
    main()
